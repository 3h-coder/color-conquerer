from constants.game_constants import BOARD_SIZE
from dto.coordinates_dto import CoordinatesDto
from dto.server_only.match_action_dto import ActionType
from game_engine.models.actions.cell_action import CellAction
from game_engine.models.cell.cell import Cell
from utils.board_utils import is_out_of_bounds


class CellMovement(CellAction):
    """
    Represents a cell moving from one cell to another
    """

    def __eq__(self, other):
        return (
            isinstance(other, CellMovement)
            and other.cell_id == self.cell_id
            and other.impacted_coords == self.impacted_coords
            and other.originating_coords == self.originating_coords
        )

    def to_dto():
        match_action_dto = super().to_dto()
        match_action_dto.type = ActionType.CELL_MOVE
        return match_action_dto

    @staticmethod
    def create(
        from_player1: bool,
        cell_id: int,
        row_index: int,
        column_index: int,
        new_row_index: int,
        new_column_index: int,
    ):
        return CellMovement(
            from_player1=from_player1,
            cell_id=cell_id,
            is_direct=True,
            impacted_coords=CoordinatesDto(new_row_index, new_column_index),
            originating_coords=CoordinatesDto(row_index, column_index),
        )

    @staticmethod
    def calculate(
        cell: Cell,
        player1: bool,
        board_array: list[list[Cell]],
        transient_board_array: list[list[Cell]],
    ):
        """
        Returns the list of movements that an owned cell can perform.
        """
        row_index, column_index = cell.row_index, cell.column_index

        movements: list[CellMovement] = []
        primary_directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # down, up, left, right
        for direction in primary_directions:
            new_row_index = row_index + direction[0]
            new_col_index = column_index + direction[1]

            if not CellMovement._is_valid_movement_target(
                new_row_index, new_col_index, cell
            ):
                continue

            target_cell: Cell = board_array[new_row_index][new_col_index]

            # Master cell extra steps
            if cell.is_master:
                movements.extend(
                    CellMovement._calculate_extra_master_movements(
                        cell, target_cell, player1, transient_board_array
                    )
                )

            if not target_cell.is_owned():
                transient_board_cell = transient_board_array[new_row_index][
                    new_col_index
                ]
                transient_board_cell.set_can_be_moved_into()

                movements.append(
                    CellMovement.create(
                        player1,
                        cell.id,
                        row_index,
                        column_index,
                        new_row_index,
                        new_col_index,
                    )
                )

        return set(movements)

    @staticmethod
    def _calculate_extra_master_movements(
        master_cell: Cell,
        target_cell: Cell,
        player1: bool,
        board_array: list[list[Cell]],
        transient_board_array: list[list[Cell]],
    ):
        """
        Gets the additional movements that a master cell may perform from a primary direction
        neighbour cell.
        """
        additional_movements = CellMovement.calculate(
            target_cell, player1, board_array, transient_board_array
        )
        return [
            CellMovement.create(
                player1,
                master_cell.id,
                master_cell.row_index,
                master_cell.column_index,
                move.impacted_coords.rowIndex,
                move.impacted_coords.columnIndex,
            )
            for move in additional_movements
        ]

    @staticmethod
    def _is_valid_movement_target(
        row_index, col_index, cell_to_move: Cell, board_array: list[list[Cell]]
    ):
        """
        A valid movement target is :

        • Not out of bounds

        • Not an owned cell if cell_to_move is not the master cell

        • Not an enemy cell if cell_to_move is the master cell
        """

        if CellMovement._is_out_of_bounds(row_index) or CellMovement._is_out_of_bounds(
            col_index
        ):
            return False

        target_cell: Cell = board_array[row_index][col_index]

        if cell_to_move.is_master:
            return not target_cell.is_hostile_to(cell_to_move)

        else:
            return not target_cell.is_owned()

    @staticmethod
    def _is_out_of_bounds(index: int):
        return is_out_of_bounds(index, board_size=BOARD_SIZE)
