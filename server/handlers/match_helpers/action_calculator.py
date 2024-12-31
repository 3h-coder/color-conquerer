import functools
from config.logging import get_configured_logger
from constants.match_constants import BOARD_SIZE
from dto.server_only.cell_info_dto import CellInfoDto
from dto.server_only.match_action_dto import MatchActionDto
from dto.server_only.match_info_dto import MatchInfoDto
from utils.board_utils import (
    copy_board,
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

    def calculate_possible_movements(
        self,
        cell: CellInfoDto,
        player1: bool,
        transient_board_array: list[list[CellInfoDto]],
    ):
        """
        Returns the list of movements that an owned cell can perform.
        """
        row_index, column_index = cell.rowIndex, cell.columnIndex

        movements: list[MatchActionDto] = []
        primary_directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # down, up, left, right
        for direction in primary_directions:
            new_row_index = row_index + direction[0]
            new_col_index = column_index + direction[1]

            if (
                _is_out_of_bounds(new_row_index)
                or _is_out_of_bounds(new_col_index)
                or (
                    is_owned(new_row_index, new_col_index, self._board_array)
                    and not cell.isMaster
                )
            ):
                continue

            corresponding_cell: CellInfoDto = self._board_array[new_row_index][
                new_col_index
            ]
            if cell.isMaster and not corresponding_cell.is_hostile_to(cell):
                self._logger.debug(
                    f"Trying to get the additional movements as the cell is master"
                )
                additional_movements = self.calculate_possible_movements(
                    corresponding_cell, player1, transient_board_array
                )
                self._logger.debug(
                    f"Found {len(additional_movements)} additional movements"
                )
                for movement in additional_movements:
                    movements.append(
                        MatchActionDto.cell_movement(
                            player1,
                            cell.id,
                            row_index,
                            column_index,
                            movement.impactedCoords[0].rowIndex,
                            movement.impactedCoords[0].columnIndex,
                        )
                    )

            if corresponding_cell.is_owned():
                continue

            transient_board_cell = transient_board_array[new_row_index][new_col_index]
            transient_board_cell.set_can_be_moved_into()

            movements.append(
                MatchActionDto.cell_movement(
                    player1,
                    cell.id,
                    row_index,
                    column_index,
                    new_row_index,
                    new_col_index,
                )
            )

        self._logger.debug(f"Returning {len(movements)} movements")
        return movements

    def _get_extra_movements_if_cell_is_master(
        self,
        cell: CellInfoDto,
        player1: bool,
        transient_board_array: list[list[CellInfoDto]],
        movements: list[MatchActionDto],
        neighbour_cell: CellInfoDto,
    ):
        if not cell.isMaster or neighbour_cell.is_hostile_to(cell):
            return

        additional_movements = self.calculate_possible_movements(
            neighbour_cell,
            player1,
            transient_board_array,
        )
        self._logger.debug(
            f"Found {len(additional_movements)} additonal movements for the corresponding cell"
            f"at ({neighbour_cell.rowIndex}, {neighbour_cell.columnIndex})"
        )
        for movement in additional_movements:

            movements.append(
                MatchActionDto.cell_movement(
                    player1,
                    cell.id,
                    cell.rowIndex,
                    cell.columnIndex,
                    movement.impactedCoords[0].rowIndex,
                    movement.impactedCoords[0].columnIndex,
                )
            )

    def calculate_possible_attacks(
        self,
        cell: CellInfoDto,
        player1: bool,
        transient_board_array: list[list[CellInfoDto]],
    ):
        """
        Returns the list of attacks that an owned cell can perform.
        """
        row_index, column_index = cell.rowIndex, cell.columnIndex

        attacks: list[MatchActionDto] = []
        neighbours: list[CellInfoDto] = get_neighbours(
            cell.rowIndex, cell.columnIndex, self._board_array
        )
        for neighbour in neighbours:
            if not cell.is_hostile_to(neighbour):
                continue

            transient_board_cell = transient_board_array[neighbour.rowIndex][
                neighbour.columnIndex
            ]
            transient_board_cell.set_can_be_attacked()

            attacks.append(
                MatchActionDto.cell_attack(
                    player1,
                    cell.id,
                    row_index,
                    column_index,
                    neighbour.rowIndex,
                    neighbour.columnIndex,
                )
            )
        return attacks

    def calculate_possible_spawns(
        self, player1: bool, transient_board_array: list[list[CellInfoDto]]
    ):
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

                transient_board_cell = transient_board_array[neighbour.rowIndex][
                    neighbour.columnIndex
                ]
                transient_board_cell.set_can_be_spawned_into()

                possible_spawns.add(
                    MatchActionDto.cell_spawn(
                        player1,
                        neighbour.rowIndex,
                        neighbour.columnIndex,
                    )
                )

        return possible_spawns


def _is_out_of_bounds(index: int):
    return is_out_of_bounds(index, board_size=BOARD_SIZE)
