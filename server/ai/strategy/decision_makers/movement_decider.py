from typing import TYPE_CHECKING, Optional, List
from game_engine.models.actions.cell_movement import CellMovement
from game_engine.action_calculation import get_possible_movements_and_attacks
from ai.strategy.decision_makers.base_decider import BaseDecider
from utils.perf_utils import with_performance_logging
from utils.board_utils import manhattan_distance

if TYPE_CHECKING:
    from handlers.match_handler_unit import MatchHandlerUnit
    from ai.strategy.evaluators.board.board_evaluation import BoardEvaluation
    from game_engine.models.cell.cell import Cell


class MovementDecider(BaseDecider):
    """
    Decision maker for cell movement.
    Determines if and where units should move.
    """

    @with_performance_logging
    def decide_movement(
        self,
        board_evaluation: "BoardEvaluation",
    ) -> Optional[CellMovement]:
        """
        Calculates the best movement action available.
        """
        transient_board = self._get_transient_board()
        turn_state = self._match.turn_state

        ai_cells = self._get_ai_cells()
        all_possible_movements: List[CellMovement] = []

        for cell in ai_cells:
            options = get_possible_movements_and_attacks(
                self._ai_is_player1, cell, transient_board, turn_state
            )
            for option in options:
                if isinstance(option, CellMovement):
                    all_possible_movements.append(option)

        if not all_possible_movements:
            return None

        best_move = None
        max_score = -1

        for move in all_possible_movements:
            score = self._score_movement(move, board_evaluation)
            if score > max_score:
                max_score = score
                best_move = move

        return best_move

    def _get_ai_cells(self) -> List["Cell"]:
        """Returns all cells belonging to the AI."""
        board = self._match_context.game_board
        all_cells = board.get_all_cells()
        return [
            cell
            for cell in all_cells
            if cell.belongs_to_player_1() == self._ai_is_player1 and cell.is_owned()
        ]

    def _score_movement(
        self, move: CellMovement, evaluation: "BoardEvaluation"
    ) -> float:
        """
        Scores a movement action.
        Primary goal: Get closer to the enemy master.
        """
        score = 0.0
        origin = move.metadata.originating_coords
        target = move.metadata.impacted_coords
        enemy_master = evaluation.enemy_master_coords

        # Calculate Manhattan distance change
        dist_before = manhattan_distance(
            origin.row_index,
            origin.column_index,
            enemy_master.row_index,
            enemy_master.column_index,
        )
        dist_after = manhattan_distance(
            target.row_index,
            target.column_index,
            enemy_master.row_index,
            enemy_master.column_index,
        )

        # Reward moving closer
        score += (dist_before - dist_after) * 10.0

        # Small bonus for moving towards the center/frontline if already close
        # (This avoids units just standing still if they can't get closer)
        if dist_after == dist_before:
            score += 1.0

        return score
