from enum import IntEnum
from typing import TYPE_CHECKING

from constants.match_constants import BOARD_SIZE
from dto.cell_info_dto import CellInfoDto
from dto.match_action_dto import MatchActionDto
from dto.possible_actions_dto import PossibleActionsDto
from handlers.match_helpers.client_notifications import notify_possible_actions
from handlers.match_helpers.service_base import ServiceBase
from utils.board_utils import get_neighbours, is_out_of_bounds, is_owned

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


class MatchActionsService(ServiceBase):
    """
    Helper class responsible for handling action requests from each players.
    The class handles both the action validation and action processing.
    """

    def __init__(self, match_handler_unit: "MatchHandlerUnit"):
        super().__init__(match_handler_unit)
        self._boardArray = self.match.match_info.boardArray
        # Dictionary storing all of the actions that happened during a match.
        # Key : turn number | Value : list of actions (type : [TBD])
        self.actions: dict[int, list] = {}
        # used to track all the actions performed during the turn
        self._turn_actions: list = []
        # Used to confirm whether an action can be done or not
        self._possible_actions: set = set()
        self._player_mode = PlayerMode.OWN_CELL_SELECTION
        self._server_mode = ServerMode.SHOW_POSSIBLE_ACTIONS

    def reset_for_new_turn(self):
        """
        Performs all the cleanup and reset necessary for a fresh new turn.
        """
        self._turn_actions = []
        self._possible_actions = set()
        self._player_mode = PlayerMode.OWN_CELL_SELECTION
        self._server_mode = ServerMode.SHOW_POSSIBLE_ACTIONS

    def handle_cell_selection(self, cell_row: int, cell_col: int):
        """
        Handles the selection of a cell. This can either trigger an action or return a list of possible actions.
        """
        # Todo
        player = self.match.get_current_player()
        player_id = player.playerId
        cell = self._boardArray[cell_row][cell_col]

        if cell.belongs_to(player):
            self._handle_owned_cell_selection(cell, player_id)

        # the cell belongs to the opponent
        elif cell.is_owned():
            # handle attack or spell
            self._handle_opponent_cell_selection(cell, player_id)

        # the cell is idle
        else:
            self._handle_idle_cell_selection(cell, player_id)

        self._send_notification()

    def _handle_owned_cell_selection(self, cell: CellInfoDto, player_id: str):
        """
        Populates the possible actions field based on the current player mode.

        For example, if the player mode is set to owned cell selection, than the possible actions are either
        move, attack, or no action.
        """
        if self._player_mode == PlayerMode.OWN_CELL_SELECTION:
            # TODO check if the cell is allowed to move
            movements = self._calculate_possible_movements(cell, player_id)
            # TODO check if the cell is allowed to attack
            attacks = self._calculate_possible_attacks(cell, player_id)

            self._set_possible_actions(movements + attacks)
            self._player_mode = PlayerMode.OWN_CELL_SELECTED

        elif self._player_mode == PlayerMode.OWN_CELL_SELECTED:
            pass  # nothing for now

        elif self._player_mode == PlayerMode.SPELL_SELECTED:
            pass  # nothing for now

    def _handle_opponent_cell_selection(self, cell: CellInfoDto, player_id: str):
        """
        Populates the possible actions field based on the current player mode.

        For example, if the player mode is set to owned cell selection, than there
        shouldn't be any possible action.
        """
        pass

    def _handle_idle_cell_selection(self, cell: CellInfoDto, player_id: str):
        """
        Populates the possible actions field based on the current player mode.

        For example, if the player mode is set to cell spawn, than there may be a spawn action.
        """
        pass

    def _send_notification(self):
        """
        Crucial method.

        Let's the client know the server's response to the player's request allowing it to render
        subsequent animations properly.
        """
        if self._server_mode == ServerMode.SHOW_POSSIBLE_ACTIONS:
            self.logger.debug(
                f"Sending to the client the possible actions : {self._possible_actions}"
            )
            # sets cannot be json serialized, hence the list() constructor
            notify_possible_actions(PossibleActionsDto(list(self._possible_actions)))
        else:
            pass

    def _set_possible_actions(self, actions: list[MatchActionDto]):
        """
        Stores all of the possible actions and sets the server mode accordingly.
        """
        self._server_mode = ServerMode.SHOW_POSSIBLE_ACTIONS
        self._possible_actions = set(actions)

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
