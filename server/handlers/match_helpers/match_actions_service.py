from enum import IntEnum
from typing import TYPE_CHECKING

from constants.match_constants import BOARD_SIZE
from dto.cell_info_dto import CellInfoDto, CellOwner, CellState
from dto.coordinates_dto import CoordinatesDto
from dto.match_action_dto import ActionType, MatchActionDto
from handlers.match_helpers.service_base import ServiceBase
from utils.board_utils import get_neighbours, is_out_of_bounds, is_owned

if TYPE_CHECKING:
    from handlers.match_helpers.match_handler_unit import MatchHandlerUnit


class PlayerMode(IntEnum):
    CELL_SELECTION = 0  # In this mode, an action is only possible on an owned cell (typically a move or attack)
    CELL_SPAWN = 1  # In this mode, a spawn action is being awaited on an idle cell
    SPELL_SELECTION = 2  # In this mode, an action is possible on any cell as this depends on the spell


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
        self._turn_actions = (
            []
        )  # used to track all the actions performed during the turn
        self._possible_actions: set = (
            None  # Used to confirm whether an action can be done or not
        )
        self._player_mode: PlayerMode = PlayerMode.CELL_SELECTION

    def reset_for_new_turn(self):
        """
        Performs all the cleanup and reset necessary for a fresh new turn.
        """
        self._turn_actions = []
        self._possible_actions = None
        self._player_mode = PlayerMode.CELL_SELECTION

    def handle_cell_selection(self, cell_row: int, cell_col: int):
        """
        Handles the selection of a cell. This can either trigger an action or return a list of possible actions.
        """
        player_id = self.match.get_current_player().playerId
        cell = self._boardArray[cell_row][cell_col]
        if cell.state == CellState.OWNED:
            self._handle_owned_cell_selection(cell, player_id)
        else:
            # handle attack or spell
            pass

    def _handle_owned_cell_selection(self, cell: CellInfoDto, player_id: str):
        """
        Populates the appropriate fields based on the current player mode.

        For example, if the player mode is set to cell selection, than an owned cell that is selected can either move or attack.
        """
        if self._player_mode == PlayerMode.CELL_SELECTION:
            # TODO check if the cell is allowed to move
            movements = self._calculate_possible_movements(cell, player_id)
            # TODO check if the cell is allowed to attack
            attacks = self._calculate_possible_attacks(cell, player_id)
            self._possible_actions = set(*movements, *attacks)
        elif self._player_mode == PlayerMode.SPELL_SELECTION:
            pass  # nothing for now

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
