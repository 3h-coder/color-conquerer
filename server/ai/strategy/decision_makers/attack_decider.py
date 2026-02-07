from typing import TYPE_CHECKING, Optional, List
from game_engine.models.actions.cell_attack import CellAttack
from game_engine.action_calculation import get_possible_movements_and_attacks
from ai.strategy.decision_makers.base_decider import BaseDecider
from utils.perf_utils import with_performance_logging

if TYPE_CHECKING:
    from handlers.match_handler_unit import MatchHandlerUnit
    from ai.strategy.evaluators.board.board_evaluation import BoardEvaluation
    from game_engine.models.cell.cell import Cell


class AttackDecider(BaseDecider):
    """
    Decision maker for cell attacks.
    Determines if any units should attack and which targets.
    """

    @with_performance_logging
    def decide_attack(
        self,
        board_evaluation: "BoardEvaluation",
    ) -> Optional[CellAttack]:
        """
        Calculates the best attack action available.
        Prioritizes:
        1. Lethal on enemy master
        2. Damage to enemy master
        3. Attacks on high-value enemy cells
        """
        transient_board = self._get_transient_board()
        turn_state = self._match.turn_state

        # 1. Gather all potential attacks
        ai_cells = self._get_ai_cells()
        all_possible_attacks: List[CellAttack] = []

        for cell in ai_cells:
            # Note: We use the real board for availability check since transient_board is a copy
            # But we pass transient_board to the calculation if it needs it (it shouldn't for attacks)
            options = get_possible_movements_and_attacks(
                self._ai_is_player1, cell, transient_board, turn_state
            )
            for option in options:
                if isinstance(option, CellAttack):
                    all_possible_attacks.append(option)

        if not all_possible_attacks:
            return None

        # 2. Check for lethal on enemy master
        # (This is handled by prioritization in _score_attack but could be explicit)

        # 3. Score and pick the best attack
        best_attack = None
        max_score = -1

        for attack in all_possible_attacks:
            score = self._score_attack(attack, board_evaluation)
            if score > max_score:
                max_score = score
                best_attack = attack

        return best_attack

    def _get_ai_cells(self) -> List["Cell"]:
        """Returns all cells belonging to the AI from the current match context."""
        board = self._match_context.game_board
        all_cells = board.get_all_cells()
        return [
            cell
            for cell in all_cells
            if cell.belongs_to_player_1() == self._ai_is_player1 and cell.is_owned()
        ]

    def _score_attack(self, attack: CellAttack, evaluation: "BoardEvaluation") -> float:
        """
        Calculates a priority score for an attack.
        """
        score = 0.0
        target_coords = attack.metadata.impacted_coords

        # High Priority: Attack enemy master
        if target_coords == evaluation.enemy_master_coords:
            score += 1000.0

            # Additional bonus if it's potentially lethal
            if evaluation.ai_has_lethal_opportunity():
                score += 500.0

        # Normal Priority: Attack enemy units
        else:
            score += 100.0

            # Simple heuristic: prioritize attacking units near our master
            # (Future: Use CellEvaluator.evaluate_target_cell)
            target_cell = self._match_context.game_board.get(
                target_coords.row_index, target_coords.column_index
            )
            if target_cell in evaluation.enemy_cells_near_ai_master:
                score += 50.0

            # Bonus for targets with low HP (to clear them)
            if target_cell.resources.current_hp <= 1:
                score += 30.0

        return score
