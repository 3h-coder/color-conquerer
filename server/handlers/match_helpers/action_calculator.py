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

            if not self._is_valid_movement_target(new_row_index, new_col_index, cell):
                continue

            target_cell: CellInfoDto = self._board_array[new_row_index][new_col_index]

            # Master cell extra steps
            if cell.isMaster and not target_cell.is_hostile_to(cell):
                movements.extend(
                    self._calculate_extra_master_movements(
                        cell, target_cell, player1, transient_board_array
                    )
                )

            # Ordinary cell steps
            if not target_cell.is_owned():
                transient_board_cell = transient_board_array[new_row_index][
                    new_col_index
                ]
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

        return movements

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

    def _calculate_extra_master_movements(
        self,
        master_cell: CellInfoDto,
        target_cell: CellInfoDto,
        player1: bool,
        transient_board_array: list[list[CellInfoDto]],
    ):
        """
        Gets the additional movements that a master cell may perform from a primary direction
        neighbour cell.
        """
        additional_movements = self.calculate_possible_movements(
            target_cell, player1, transient_board_array
        )
        return [
            MatchActionDto.cell_movement(
                player1,
                master_cell.id,
                master_cell.rowIndex,
                master_cell.columnIndex,
                move.impactedCoords[0].rowIndex,
                move.impactedCoords[0].columnIndex,
            )
            for move in additional_movements
        ]

    def _is_valid_movement_target(
        self, row_index, col_index, cell_to_move: CellInfoDto
    ):
        """
        A valid movement target is :

        • Not out of bounds

        • Not an owned cell, unless cell_to_move is the master cell, in which case we will need further checks.
        """
        return (
            not _is_out_of_bounds(row_index)
            and not _is_out_of_bounds(col_index)
            and (
                not is_owned(row_index, col_index, self._board_array)
                or cell_to_move.isMaster
            )
        )


def _is_out_of_bounds(index: int):
    return is_out_of_bounds(index, board_size=BOARD_SIZE)
