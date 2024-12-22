from enum import IntEnum, StrEnum
from typing import TYPE_CHECKING

from config.logging import get_configured_logger
from constants.match_constants import BOARD_SIZE
from dto.match_action_dto import MatchActionDto
from dto.possible_actions_dto import PossibleActionsDto
from dto.processed_actions_dto import ProcessedActionsDto
from dto.server_only.cell_info_dto import CellInfoDto
from handlers.match_helpers.action_processor import ActionProcessor
from handlers.match_helpers.client_notifications import (
    notify_action_error,
    notify_possible_actions,
    notify_processed_actions,
)
from handlers.match_helpers.service_base import ServiceBase
from utils.board_utils import (
    get_neighbours,
    is_out_of_bounds,
    is_owned,
    to_client_board_dto,
)

if TYPE_CHECKING:
    from handlers.match_helpers.match_handler_unit import MatchHandlerUnit


class PlayerMode(IntEnum):
    # Default, the player is expected to select a cell of his own
    OWN_CELL_SELECTION = 0
    # The player just selected a cell of his own and is expected to perform an action from it (move or attack)
    OWN_CELL_SELECTED = 1
    # A spawn action is being awaited on an idle cell with no owner
    CELL_SPAWN = 2
    # The player selected a spell, an action is possible on any cell as this depends on the spell
    SPELL_SELECTED = 3


class ServerMode(IntEnum):
    # The server intends to show the possible actions to the player whose turn it is
    SHOW_POSSIBLE_ACTIONS = 0
    # The server intends to show the processed actions to both players
    SHOW_PROCESSED_ACTIONS = 1


class ErrorMessages(StrEnum):
    CANNOT_MOVE_TO_NOR_ATTACK = "Cannot move to nor attack this cell"
    INVALID_ACTION = "Invalid action"  # The client should prevent this message from being shown, but just in case


class MatchActionsService(ServiceBase):
    """
    Helper class responsible for handling action requests from each players.
    The class handles both the action validation and action processing.
    """

    def __init__(self, match_handler_unit: "MatchHandlerUnit"):
        super().__init__(match_handler_unit)
        self._logger = get_configured_logger(__name__)

        self._boardArray = self.match.match_info.boardArray
        self._action_processor = ActionProcessor(self.match_info)
        # Dictionary storing all of the actions that happened during a match.
        # Key : turn number | Value : list of actions (type : [TBD])
        self.actions: dict[int, list] = {}
        # used to track all the actions performed during the turn
        self._turn_actions: list = []
        # Used to confirm whether an action can be done or not
        self._possible_actions: set = set()
        # Actions that have been validated and applied, overridden each time a set of action is processed
        self._processed_actions: set = set()
        self._player_mode = PlayerMode.OWN_CELL_SELECTION
        self._server_mode = ServerMode.SHOW_POSSIBLE_ACTIONS
        # Applicable when the player mode is OWN_CELL_SELECTED
        self._selected_cell: CellInfoDto = None
        # Message to the player when their request is invalid
        self._error_msg: str = ""

    def reset_for_new_turn(self):
        """
        Performs all the cleanup and reset necessary for a fresh new turn.

        Meant to be used as a callback for the turn watcher service.
        """
        self.actions[self.match_info.currentTurn] = []
        self._turn_actions = []
        self._reset_temporary_field_values()

    def handle_cell_selection(self, cell_row: int, cell_col: int):
        """
        Handles the selection of a cell. This can either trigger an action or return a list of possible actions.
        """
        player = self.match.get_current_player()
        player_id = player.playerId
        cell: CellInfoDto = self._boardArray[cell_row][cell_col]
        print(f"The type of cell is {type(cell)}")

        if cell.belongs_to(player):
            self._handle_own_cell_selection(cell, player_id)

        # the cell belongs to the opponent
        elif cell.is_owned():
            # handle attack or spell
            self._handle_opponent_cell_selection(cell, player_id)

        # the cell is idle
        else:
            self._handle_idle_cell_selection(cell, player_id)

        self._send_response()

        if self._server_mode == ServerMode.SHOW_PROCESSED_ACTIONS:
            self._reset_temporary_field_values()

    def _handle_own_cell_selection(self, cell: CellInfoDto, player_id: str):
        """
        Handles all possible cases resulting from a player selecting a cell of their own.

        For example, if the player mode is set to owned cell selection, than the possible actions are either
        move, attack, or no action.
        """
        if self._player_mode == PlayerMode.OWN_CELL_SELECTION:
            self._set_selected_cell(cell)
            # TODO check if the cell is allowed to move
            movements = self._calculate_possible_movements(cell, player_id)
            # TODO check if the cell is allowed to attack
            attacks = self._calculate_possible_attacks(cell, player_id)

            self._set_possible_actions(set(movements + attacks))

        elif self._player_mode == PlayerMode.OWN_CELL_SELECTED:
            if self._selected_cell == cell:
                # Cancel cell selection
                self._reset_temporary_field_values()
            elif cell.is_owned():
                self._error_msg = ErrorMessages.CANNOT_MOVE_TO_NOR_ATTACK

        elif self._player_mode == PlayerMode.SPELL_SELECTED:
            pass  # nothing for now

    def _handle_opponent_cell_selection(self, cell: CellInfoDto, player_id: str):
        """
        Handles all possible cases resulting from a player selecting an enemy cell of their own.

        For example, if the player mode is set to owned cell selection, than there
        shouldn't be any possible action.
        """
        pass

    def _handle_idle_cell_selection(self, cell: CellInfoDto, player_id: str):
        """
        Handles all possible cases resulting from a player selecting an idle cell.

        For example, if the player mode is set to cell spawn, than there may be a spawn action.
        """
        if self._player_mode == PlayerMode.OWN_CELL_SELECTION:
            self._error_msg = ErrorMessages.INVALID_ACTION

        elif self._player_mode == PlayerMode.OWN_CELL_SELECTED:
            movement = MatchActionDto.cell_movement(
                player_id,
                self._selected_cell.rowIndex,
                self._selected_cell.columnIndex,
                cell.rowIndex,
                cell.columnIndex,
            )
            if movement not in self._possible_actions:
                self._error_msg = ErrorMessages.INVALID_ACTION
            else:
                self._process_actions([movement])

    def _send_response(self):
        """
        Crucial method.

        Let's the client know the server's response to the player's request allowing it to render
        subsequent animations properly.
        """
        if self._error_msg:
            notify_action_error(self._error_msg)
            return

        if self._server_mode == ServerMode.SHOW_POSSIBLE_ACTIONS:
            self._logger.debug(
                f"Sending to the client the possible actions : {self._possible_actions}"
            )
            # sets cannot be json serialized, hence the list() constructor
            notify_possible_actions(PossibleActionsDto(list(self._possible_actions)))
        elif self._server_mode == ServerMode.SHOW_PROCESSED_ACTIONS:
            self._logger.debug(
                f"Sending to the client the processed actions: {self._processed_actions}"
            )
            notify_processed_actions(
                ProcessedActionsDto(
                    list(self._processed_actions), to_client_board_dto(self._boardArray)
                ),
                self.room_id,
            )

    def _reset_temporary_field_values(self):
        self._player_mode = PlayerMode.OWN_CELL_SELECTION
        self._server_mode = ServerMode.SHOW_POSSIBLE_ACTIONS
        self._possible_actions = set()
        self._processed_actions = set()
        self._selected_cell = None
        self._error_msg = ""

    def _set_possible_actions(self, actions: set[MatchActionDto]):
        """
        Stores all of the possible actions and sets the server mode accordingly.
        """
        self._server_mode = ServerMode.SHOW_POSSIBLE_ACTIONS
        self._possible_actions = actions

    def _process_actions(self, actions: set[MatchActionDto]):
        """
        Processes all of the given actions, setting the associate fields along the way.
        """
        self._server_mode = ServerMode.SHOW_PROCESSED_ACTIONS
        processed_actions = self._action_processor.process_actions_sequentially(actions)
        self._processed_actions = processed_actions
        self._register_processed_actions(processed_actions)

    def _register_processed_actions(self, actions: set[MatchActionDto]):
        """
        Adds a processed action to the turn and match actions fields.
        """
        current_turn = self.match_info.currentTurn
        if current_turn not in self.actions:
            self.actions[current_turn] = []

        for action in actions:
            self.actions[current_turn].append(action)
            self._turn_actions.append(action)

    def _set_selected_cell(self, cell: CellInfoDto):
        """
        Sets the player mode and selected cell fields accordingly.
        """
        self._player_mode = PlayerMode.OWN_CELL_SELECTED
        self._selected_cell = cell

    def _calculate_possible_movements(self, cell: CellInfoDto, player_id: str):
        """
        Returns the list of movements that an owned cell can perform.
        """
        row_index, column_index = cell.rowIndex, cell.columnIndex

        movements = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # down, up, left, right
        for direction in directions:
            new_row_index = row_index + direction[0]
            new_col_index = column_index + direction[1]
            if (
                _is_out_of_bounds(new_row_index)
                or _is_out_of_bounds(new_col_index)
                or is_owned(new_row_index, new_col_index, self._boardArray)
            ):
                continue

            movements.append(
                MatchActionDto.cell_movement(
                    player_id, row_index, column_index, new_row_index, new_col_index
                )
            )

        return movements

    def _calculate_possible_attacks(self, cell: CellInfoDto, player_id: str):
        """
        Returns the list of attacks that an owned cell can perform.
        """
        row_index, column_index = cell.rowIndex, cell.columnIndex

        attacks = []
        neighbours: list[CellInfoDto] = get_neighbours(
            cell.rowIndex, cell.columnIndex, self._boardArray
        )
        for neighbour in neighbours:
            if cell.is_hostile_to(neighbour):
                attacks.append(
                    MatchActionDto.cell_attack(
                        player_id,
                        row_index,
                        column_index,
                        neighbour.rowIndex,
                        neighbour.columnIndex,
                    )
                )
        return attacks


def _is_out_of_bounds(index: int):
    return is_out_of_bounds(index, board_size=BOARD_SIZE)
