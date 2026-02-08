from typing import TYPE_CHECKING
from game_engine.models.dtos.coordinates import Coordinates
from ai.config.ai_config import (
    ATTACK_WEIGHT_BASE_ATTACK,
    ATTACK_WEIGHT_THREAT_DEFENSE,
    ATTACK_WEIGHT_LOW_HP_BONUS,
    ATTACK_WEIGHT_ENEMY_MASTER,
    ATTACK_WEIGHT_LETHAL_ON_MASTER,
    ATTACK_WEIGHT_ARCHER_TARGET_BONUS,
    ATTACK_WEIGHT_MASTER_RETALIATION_PENALTY,
)
from ai.strategy.evaluators.base_evaluator import BaseEvaluator

if TYPE_CHECKING:
    from ai.strategy.evaluators.board.board_evaluation import BoardEvaluation
    from game_engine.models.cell.cell import Cell


class AttackEvaluator(BaseEvaluator):
    """
    Evaluates enemy cells as potential attack targets.
    """

    def evaluate(
        self,
        target_coords: Coordinates,
        board_evaluation: "BoardEvaluation",
        attacker_coords: Coordinates | None = None,
    ) -> float:
        """
        Calculates a score for an enemy cell as an attack target.
        """
        # High priority: attacking enemy master is always best
        if target_coords == board_evaluation.enemy_master_coords:
            return self._evaluate_master_attack(board_evaluation)

        # Normal priority: evaluate regular unit attacks
        score = ATTACK_WEIGHT_BASE_ATTACK

        target_cell = self._match_context.game_board.get(
            target_coords.row_index, target_coords.column_index
        )

        if not target_cell:
            return 0.0

        score += self._evaluate_master_retaliation_penalty(attacker_coords)
        score += self._evaluate_threat_defense(target_cell, board_evaluation)
        score += self._evaluate_archer_elimination(target_cell)
        score += self._evaluate_kill_potential(target_cell)

        return score

    def _evaluate_master_attack(self, board_evaluation: "BoardEvaluation") -> float:
        """
        Attacking the enemy master is the highest priority.
        Bonus if the attack is potentially lethal.
        """
        score = ATTACK_WEIGHT_ENEMY_MASTER

        if board_evaluation.ai_has_lethal_opportunity():
            score += ATTACK_WEIGHT_LETHAL_ON_MASTER

        return score

    def _evaluate_master_retaliation_penalty(
        self, attacker_coords: Coordinates | None
    ) -> float:
        """
        If the attacker is our master and target is NOT the enemy master, penalize it.
        Master should avoid attacking non-masters (loses HP unnecessarily).
        """
        if not attacker_coords:
            return 0.0

        attacker_cell = self._match_context.game_board.get(
            attacker_coords.row_index, attacker_coords.column_index
        )
        if attacker_cell and attacker_cell.is_master:
            return ATTACK_WEIGHT_MASTER_RETALIATION_PENALTY

        return 0.0

    def _evaluate_threat_defense(
        self, target_cell: "Cell", board_evaluation: "BoardEvaluation"
    ) -> float:
        """
        Prioritize targets that are threats near our master.
        """
        if target_cell in board_evaluation.enemy_cells_near_ai_master:
            return ATTACK_WEIGHT_THREAT_DEFENSE
        return 0.0

    def _evaluate_archer_elimination(self, target_cell: "Cell") -> float:
        """
        Archers are high-priority threats - eliminate before they establish range dominance.
        """
        if target_cell.is_archer():
            return ATTACK_WEIGHT_ARCHER_TARGET_BONUS
        return 0.0

    def _evaluate_kill_potential(self, target_cell: "Cell") -> float:
        """
        Non-shielded cells are easier to kill.
        """
        if not target_cell.is_shielded():
            return ATTACK_WEIGHT_LOW_HP_BONUS
        return 0.0
