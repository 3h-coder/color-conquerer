from constants.game_constants import BOARD_SIZE
from dto.actions.match_action_dto import ActionType
from game_engine.models.actions.action import Action
from game_engine.models.actions.callbacks.action_callback_id import ActionCallBackId
from game_engine.models.actions.cell_action import CellAction
from game_engine.models.actions.hooks.mana_bubble_hook import ManaBubbleHook
from game_engine.models.cell.cell import Cell
from game_engine.models.dtos.coordinates import Coordinates
from game_engine.models.game_board import GameBoard
from game_engine.models.dtos.match_context import MatchContext
from utils.board_utils import is_out_of_bounds


class CellMovement(CellAction):
    """
    Represents a cell moving from one cell to another
    """

    HOOKS = {ManaBubbleHook()}
    CALLBACKS = {ActionCallBackId.MINE_EXPLOSION}

    def __eq__(self, other):
        return (
            isinstance(other, CellMovement)
            and other.cell_id == self.cell_id
            and other.metadata == self.metadata
        )

    def __hash__(self):
        return hash((self.cell_id, self.metadata))

    def __repr__(self):
        return (
            f"<CellMovement(from_player1={self.from_player1}, "
            f"cell_id={self.cell_id}, "
            f"mana_cost={self.mana_cost}, "
            f"metadata={self.metadata}, "
            f"callbacks_to_trigger={self._callbacks_to_trigger})>"
        )

    def to_dto(self):
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
            impacted_coords=Coordinates(new_row_index, new_column_index),
            originating_coords=Coordinates(row_index, column_index),
        )

    @staticmethod
    def calculate(
        cell: Cell,
        player1: bool,
        transient_game_board: GameBoard,
        allow_extra_movements: bool = True,
    ):
        """
        Returns the list of movements that an owned cell can perform.
        """
        row_index, column_index = cell.row_index, cell.column_index

        movements: set[CellMovement] = set()
        primary_directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # down, up, left, right
        for direction in primary_directions:
            new_row_index = row_index + direction[0]
            new_col_index = column_index + direction[1]

            if not CellMovement._is_valid_movement_target(
                new_row_index,
                new_col_index,
                cell,
                transient_game_board,
            ):
                continue

            target_cell: Cell = transient_game_board.get(new_row_index, new_col_index)

            if allow_extra_movements:
                movements = movements.union(
                    CellMovement._calculate_extra_movements(
                        cell, target_cell, player1, transient_game_board
                    )
                )

            if not target_cell.is_owned():
                transient_board_cell = transient_game_board.get(
                    new_row_index, new_col_index
                )
                transient_board_cell.set_can_be_moved_into()

                movements.add(
                    CellMovement.create(
                        player1,
                        cell.id,
                        row_index,
                        column_index,
                        new_row_index,
                        new_col_index,
                    )
                )

        return movements

    @Action.trigger_hooks_and_check_callbacks
    def apply(self, match_context: MatchContext):
        """
        Moves a cell from the given original coordinates to the given new coordinates.

        This method does nothing if the cell to move is idle, and leaves an idle cell at the original coordinates otherwise.
        """
        game_board = match_context.game_board
        originating_coords = self.metadata.originating_coords
        target_coords = self.metadata.impacted_coords

        cell_original_coords = game_board.get(
            originating_coords.row_index, originating_coords.column_index
        )

        if not cell_original_coords.is_owned():
            return

        cell_new_coords = game_board.get(
            target_coords.row_index, target_coords.column_index
        )
        CellMovement._transfer_cell(cell_original_coords, cell_new_coords)

    @staticmethod
    def _calculate_extra_movements(
        cell: Cell,
        target_cell: Cell,
        player1: bool,
        transient_game_board: GameBoard,
    ):
        """
        Gets the additional movements that a master cell may perform from a primary direction
        neighbour cell.
        """
        additional_movements: set[CellMovement] = CellMovement.calculate(
            target_cell, player1, transient_game_board, False
        )
        return {
            CellMovement.create(
                player1,
                cell.id,
                cell.row_index,
                cell.column_index,
                move.metadata.impacted_coords.row_index,
                move.metadata.impacted_coords.column_index,
            )
            for move in additional_movements
        }

    @staticmethod
    def _is_valid_movement_target(
        row_index,
        col_index,
        cell_to_move: Cell,
        game_board: GameBoard,
    ):
        """
        A valid movement target is:

        • Not out of bounds

        • Not an enemy cell
        """

        if CellMovement._is_out_of_bounds(row_index) or CellMovement._is_out_of_bounds(
            col_index
        ):
            return False

        target_cell = game_board.get(row_index, col_index)
        return not target_cell.is_hostile_to(cell_to_move)

    @staticmethod
    def _transfer_cell(old_cell: Cell, new_cell: Cell):
        # Information from the new cell that should be reapplied
        # after the state copy
        new_cell_coords = new_cell.get_coordinates()
        new_cell_hidden_state_info = new_cell.hidden_state_info

        new_cell.copy_state(old_cell)

        # Apply back the information that we saved
        new_cell.row_index, new_cell.column_index = new_cell_coords.as_tuple()
        new_cell.hidden_state_info = new_cell_hidden_state_info

        old_cell.kill()

    @staticmethod
    def _is_out_of_bounds(index: int):
        return is_out_of_bounds(index, board_size=BOARD_SIZE)
