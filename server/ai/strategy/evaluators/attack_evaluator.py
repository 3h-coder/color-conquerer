from typing import TYPE_CHECKING
from game_engine.models.dtos.coordinates import Coordinates
from ai.config.ai_config import (
    AttackWeights,
    HealthThresholds,
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
        Returns a negative score if the action would be suicidal (master at critical health).
        """
        # Check if master is at suicidal health level (would die from any damage)
        ai_player = (
            self._match_context.player1
            if self._ai_is_player1
            else self._match_context.player2
        )

        # If master is suicidal, mark attack with negative score UNLESS it's lethal on enemy master
        # The master should only attack the enemy master if there's a lethal opportunity,
        # meaning the combined damage from all attacking units (including this master) can kill the enemy master.
        if ai_player.resources.current_hp == HealthThresholds.SUICIDAL:
            if target_coords != board_evaluation.enemy_master_coords:
                return -1.0  # Suicidal action: don't attack non-master targets
            if not board_evaluation.ai_has_lethal_opportunity():
                return -1.0  # Suicidal action: no lethal opportunity for the team
            # Otherwise: lethal opportunity exists and master is attacking enemy master, proceed with evaluation

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
        score = AttackWeights.BASE_ATTACK

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
        score = AttackWeights.ENEMY_MASTER

        if board_evaluation.ai_has_lethal_opportunity():
            score += AttackWeights.LETHAL_ON_MASTER

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
            return AttackWeights.MASTER_RETALIATION_PENALTY

        return 0.0

    def _evaluate_threat_defense(
        self, target_cell: "Cell", board_evaluation: "BoardEvaluation"
    ) -> float:
        """
        Prioritize targets that are threats near our master.
        Significantly boost priority if master health is critical.
        """
        if target_cell in board_evaluation.enemy_cells_near_ai_master:
            score = AttackWeights.THREAT_DEFENSE

            # When master is at critical health, massively boost threat defense
            ai_player = (
                self._match_context.player1
                if self._ai_is_player1
                else self._match_context.player2
            )
            if ai_player.resources.current_hp <= HealthThresholds.CRITICAL:
                score += AttackWeights.CRITICAL_THREAT_DEFENSE

            return score
        return 0.0

    def _evaluate_archer_elimination(self, target_cell: "Cell") -> float:
        """
        Archers are high-priority threats - eliminate before they establish range dominance.
        """
        if target_cell.is_archer():
            return AttackWeights.ARCHER_TARGET_BONUS
        return 0.0

    def _evaluate_kill_potential(self, target_cell: "Cell") -> float:
        """
        Non-shielded cells are easier to kill.
        """
        if not target_cell.is_shielded():
            return AttackWeights.LOW_HP_BONUS
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

        return self._is_ai_master_critical_health()
