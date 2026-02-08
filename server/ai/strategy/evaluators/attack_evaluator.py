from typing import TYPE_CHECKING
from game_engine.models.dtos.coordinates import Coordinates
from ai.config.ai_config import (
    ATTACK_WEIGHT_BASE_ATTACK,
    ATTACK_WEIGHT_THREAT_DEFENSE,
    ATTACK_WEIGHT_LOW_HP_BONUS,
    ATTACK_WEIGHT_ENEMY_MASTER,
    ATTACK_WEIGHT_LETHAL_ON_MASTER,
)
from ai.strategy.evaluators.base_evaluator import BaseEvaluator

if TYPE_CHECKING:
    from ai.strategy.evaluators.board.board_evaluation import BoardEvaluation


class AttackEvaluator(BaseEvaluator):
    """
    Evaluates enemy cells as potential attack targets.
    """

    def evaluate(
        self,
        target_coords: Coordinates,
        board_evaluation: "BoardEvaluation",
    ) -> float:
        """
        Calculates a score for an enemy cell as an attack target.
        """
        # 1. High Priority: Attack enemy master
        if target_coords == board_evaluation.enemy_master_coords:
            score = ATTACK_WEIGHT_ENEMY_MASTER

            # Additional bonus if it's potentially lethal
            if board_evaluation.ai_has_lethal_opportunity():
                score += ATTACK_WEIGHT_LETHAL_ON_MASTER

            return score

        # 2. Normal Priority: Attack enemy units
        score = ATTACK_WEIGHT_BASE_ATTACK

        target_cell = self._match_context.game_board.get(
            target_coords.row_index, target_coords.column_index
        )

        if not target_cell:
            return 0.0

        # 3. Threat defense: Prioritize targets near our master
        if target_cell in board_evaluation.enemy_cells_near_ai_master:
            score += ATTACK_WEIGHT_THREAT_DEFENSE

        # 4. Kill potential: Bonus for non-shielded cells (easier to clear)
        if not target_cell.is_shielded():
            score += ATTACK_WEIGHT_LOW_HP_BONUS

        return score
