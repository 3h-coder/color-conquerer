from config.logging import get_configured_logger
from constants.match_constants import BOARD_SIZE
from dto.server_only.cell_info_dto import CellInfoDto
from dto.server_only.match_action_dto import MatchActionDto
from dto.server_only.match_info_dto import MatchInfoDto
from utils.board_utils import (
    get_cells_owned_by_player,
    get_neighbours,
    is_out_of_bounds,
    is_owned,
)


class ActionCalculator:
    """
    Class responsible for calculatingall of the possible actions upon a player request
    such as a cell click for example.
    """

    def __init__(self, match_info: MatchInfoDto):
        self._logger = get_configured_logger(__name__)
        self._match_info = match_info
        self._board_array = match_info.boardArray

    def calculate_possible_movements(self, cell: CellInfoDto, player_id: str):
        """
        Returns the list of movements that an owned cell can perform.
        """
        row_index, column_index = cell.rowIndex, cell.columnIndex

        movements: list[MatchActionDto] = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # down, up, left, right
        for direction in directions:
            new_row_index = row_index + direction[0]
            new_col_index = column_index + direction[1]
            if (
                _is_out_of_bounds(new_row_index)
                or _is_out_of_bounds(new_col_index)
                or is_owned(new_row_index, new_col_index, self._board_array)
            ):
                continue

            movements.append(
                MatchActionDto.cell_movement(
                    player_id,
                    cell.id,
                    row_index,
                    column_index,
                    new_row_index,
                    new_col_index,
                )
            )

        return movements

    def calculate_possible_attacks(self, cell: CellInfoDto, player_id: str):
        """
        Returns the list of attacks that an owned cell can perform.
        """
        row_index, column_index = cell.rowIndex, cell.columnIndex

        attacks: list[MatchActionDto] = []
        neighbours: list[CellInfoDto] = get_neighbours(
            cell.rowIndex, cell.columnIndex, self._board_array
        )
        for neighbour in neighbours:
            if cell.is_hostile_to(neighbour):
                attacks.append(
                    MatchActionDto.cell_attack(
                        player_id,
                        cell.id,
                        row_index,
                        column_index,
                        neighbour.rowIndex,
                        neighbour.columnIndex,
                    )
                )
        return attacks

    def calculate_possible_spawns(self, player1: bool, player_id: str):
        """
        Returns a set of spawns that a player can perform.
        """
        possible_spawns: set[MatchActionDto] = set()

        owned_cells = get_cells_owned_by_player(player1, self._board_array)
        for cell in owned_cells:
            row_index, column_index = cell.rowIndex, cell.columnIndex
            neighbours: list[CellInfoDto] = get_neighbours(
                row_index, column_index, self._board_array
            )
            for neighbour in neighbours:
                if neighbour.is_owned():
                    continue
                possible_spawns.add(
                    MatchActionDto.cell_spawn(
                        player_id,
                        neighbour.rowIndex,
                        neighbour.columnIndex,
                    )
                )

        return possible_spawns


def _is_out_of_bounds(index: int):
    return is_out_of_bounds(index, board_size=BOARD_SIZE)
