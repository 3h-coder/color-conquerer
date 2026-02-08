from typing import TYPE_CHECKING, Optional, List
from game_engine.models.actions.cell_movement import CellMovement
from game_engine.action_calculation import get_possible_movements_and_attacks
from ai.strategy.decision_makers.base_decider import BaseDecider
from utils.perf_utils import with_performance_logging
from ai.strategy.evaluators.cell_evaluator import CellEvaluator

if TYPE_CHECKING:
    from handlers.match_handler_unit import MatchHandlerUnit
    from ai.strategy.evaluators.board.board_evaluation import BoardEvaluation
    from game_engine.models.cell.cell import Cell


class MovementDecider(BaseDecider):
    """
    Decision maker for cell movement.
    Determines if and where units should move.
    """

    def __init__(self, match: "MatchHandlerUnit", ai_is_player1: bool):
        super().__init__(match, ai_is_player1)
        self._cell_evaluator = CellEvaluator(match, ai_is_player1)

    @with_performance_logging
    def decide_movement(
        self,
        board_evaluation: "BoardEvaluation",
    ) -> Optional[CellMovement]:
        """
        Calculates the best movement action available.
        """
        # 1. Setup board and state
        game_board = self._match_context.game_board
        transient_board = self._get_transient_board()
        turn_state = self._match.turn_state

        # 2. Get AI cells from the current board state
        ai_cells = game_board.get_cells_owned_by_player(player1=self._ai_is_player1)
        all_possible_movements: List[CellMovement] = []

        # 3. Consider all possible movements for each AI cell
        for cell in ai_cells:
            # Use transient board to avoid marking real board cells with transient states
            options = get_possible_movements_and_attacks(
                self._ai_is_player1, cell, transient_board, turn_state
            )
            for option in options:
                if isinstance(option, CellMovement):
                    all_possible_movements.append(option)

        if not all_possible_movements:
            return None

        # 4. Evaluate each possible move and pick the best one
        best_move = None
        max_score = -1.0

        for move in all_possible_movements:
            score = self._score_movement(move, board_evaluation)
            if score > max_score:
                max_score = score
                best_move = move

        return best_move

    def _score_movement(
        self, move: CellMovement, evaluation: "BoardEvaluation"
    ) -> float:
        """
        Scores a movement action using the CellEvaluator.
        Primary goal: Get closer to the enemy master or maintain strategic positions.
        """
        target_coords = move.metadata.impacted_coords
        return self._cell_evaluator.evaluate_movement_destination(
            target_coords, evaluation
        )
