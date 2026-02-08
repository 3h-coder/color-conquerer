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
    ATTACK_WEIGHT_CRITICAL_THREAT_DEFENSE,
    MASTER_CRITICAL_HEALTH_THRESHOLD,
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
        # Prevent master from attacking when health is critical (preserve HP)
        # UNLESS it's a guaranteed lethal attack on the enemy master
        if self._attacker_is_master_and_health_critical(attacker_coords):
            if target_coords == board_evaluation.enemy_master_coords:
                # Only allow if this will guarantee victory (lethal opportunity)
                if not board_evaluation.ai_has_lethal_opportunity():
                    return 0.0  # Don't attack - too risky, would just waste our last HP
            else:
                return 0.0  # Master doesn't attack anything else when critical

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
        Significantly boost priority if master health is critical.
        """
        if target_cell in board_evaluation.enemy_cells_near_ai_master:
            score = ATTACK_WEIGHT_THREAT_DEFENSE

            # When master is at critical health, massively boost threat defense
            ai_player = (
                self._match_context.player1
                if self._ai_is_player1
                else self._match_context.player2
            )
            if ai_player.resources.current_hp <= MASTER_CRITICAL_HEALTH_THRESHOLD:
                score += ATTACK_WEIGHT_CRITICAL_THREAT_DEFENSE

            return score
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

    def _attacker_is_master_and_health_critical(
        self, attacker_coords: Coordinates | None
    ) -> bool:
        """
        Checks if the attacker is the master and its health is at critical level.
        """
        if not attacker_coords:
            return False

        attacker_cell = self._match_context.game_board.get(
            attacker_coords.row_index, attacker_coords.column_index
        )
        if not attacker_cell or not attacker_cell.is_master:
            return False

        ai_player = (
            self._match_context.player1
            if self._ai_is_player1
            else self._match_context.player2
        )
        return ai_player.resources.current_hp <= MASTER_CRITICAL_HEALTH_THRESHOLD
