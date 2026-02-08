from typing import TYPE_CHECKING, Optional, List
from game_engine.models.actions.cell_attack import CellAttack
from game_engine.action_calculation import get_possible_movements_and_attacks
from ai.strategy.decision_makers.base_decider import BaseDecider
from ai.strategy.evaluators.attack_evaluator import AttackEvaluator
from ai.strategy.scored_action import ScoredAction

if TYPE_CHECKING:
    from handlers.match_handler_unit import MatchHandlerUnit
    from ai.strategy.evaluators.board.board_evaluation import BoardEvaluation
    from game_engine.models.cell.cell import Cell


class AttackDecider(BaseDecider):
    """
    Decision maker for cell attacks.
    Determines if any units should attack and which targets.
    """

    def __init__(self, match: "MatchHandlerUnit", ai_is_player1: bool):
        super().__init__(match, ai_is_player1)
        self._evaluator = AttackEvaluator(match, ai_is_player1)

    def decide_attack(
        self,
        board_evaluation: "BoardEvaluation",
    ) -> Optional[ScoredAction]:
        """
        Calculates the best attack action available.
        Returns a ScoredAction so the brain can compare across action types.
        """
        transient_board = self._get_transient_board()
        turn_state = self._match.turn_state

        # 1. Gather all potential attacks
        # Must use FRESH cells from the current board state, not stale board_evaluation cells
        ai_cells = self.game_board.get_cells_owned_by_player(
            player1=self._ai_is_player1
        )
        all_possible_attacks: List[CellAttack] = []

        for cell in ai_cells:
            # Use transient board to avoid marking real board cells with transient states
            options = get_possible_movements_and_attacks(
                self._ai_is_player1, cell, transient_board, turn_state
            )
            for option in options:
                if isinstance(option, CellAttack):
                    all_possible_attacks.append(option)

        # 2. Score and pick the best attack
        return self._pick_best_action(
            all_possible_attacks,
            lambda attack: self._evaluator.evaluate(
                attack.metadata.impacted_coords, board_evaluation
            ),
        )
