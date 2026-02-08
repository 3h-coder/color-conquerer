from typing import TYPE_CHECKING
from game_engine.models.dtos.coordinates import Coordinates
from utils.board_utils import manhattan_distance
from ai.config.ai_config import (
    SPAWN_WEIGHT_DISTANCE_TO_ENEMY_MASTER,
    SPAWN_WEIGHT_DISTANCE_TO_OWN_MASTER,
    BASE_SPAWN_SCORE,
    MAX_BOARD_DISTANCE,
    DEFENSIVE_SPAWN_THREAT_THRESHOLD,
    MOVE_WEIGHT_DISTANCE_TO_ENEMY_MASTER,
    MOVE_WEIGHT_DISTANCE_TO_OWN_MASTER,
    BASE_MOVE_SCORE,
    DEFENSIVE_MOVE_THREAT_THRESHOLD,
    ATTACK_WEIGHT_BASE_ATTACK,
    ATTACK_WEIGHT_THREAT_DEFENSE,
    ATTACK_WEIGHT_LOW_HP_BONUS,
    ATTACK_WEIGHT_ENEMY_MASTER,
    ATTACK_WEIGHT_LETHAL_ON_MASTER,
)
from ai.strategy.evaluators.base_evaluator import BaseEvaluator

if TYPE_CHECKING:
    from ai.strategy.evaluators.board.board_evaluation import BoardEvaluation


class CellEvaluator(BaseEvaluator):
    """
    Evaluates individual cells or board positions for strategic value.
    Used by decision makers to prioritize targets, movement destinations, and spawn locations.
    """

    def evaluate_spawn_location(
        self,
        coords: Coordinates,
        board_evaluation: "BoardEvaluation",
    ) -> float:
        """
        Calculates a score for a potential spawn location.
        Higher scores indicate better locations.
        """
        score = BASE_SPAWN_SCORE

        # 1. Distance to enemy master (closer is better for pressure)
        dist_to_enemy = manhattan_distance(
            coords.row_index,
            coords.column_index,
            board_evaluation.enemy_master_coords.row_index,
            board_evaluation.enemy_master_coords.column_index,
        )
        # Using a simple inverse relationship: score increases as distance decreases
        score += (
            MAX_BOARD_DISTANCE - dist_to_enemy
        ) * SPAWN_WEIGHT_DISTANCE_TO_ENEMY_MASTER

        # 2. Distance to own master (closer is better for defense if threatened)
        if board_evaluation.master_threat_level > DEFENSIVE_SPAWN_THREAT_THRESHOLD:
            dist_to_own = manhattan_distance(
                coords.row_index,
                coords.column_index,
                board_evaluation.ai_master_coords.row_index,
                board_evaluation.ai_master_coords.column_index,
            )
            # Prioritize blocking or defending when threatened
            score += (
                MAX_BOARD_DISTANCE - dist_to_own
            ) * SPAWN_WEIGHT_DISTANCE_TO_OWN_MASTER

        return score

    def evaluate_target_cell(
        self,
        target_coords: Coordinates,
        board_evaluation: "BoardEvaluation",
    ) -> float:
        """
        Calculates a score for an enemy cell as an attack target.
        Used by AttackDecider.
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

    def evaluate_movement_destination(
        self,
        dest_coords: Coordinates,
        board_evaluation: "BoardEvaluation",
    ) -> float:
        """
        Calculates a score for a movement destination.
        Used by MovementDecider.
        """
        # 1. Start with base score
        score = BASE_MOVE_SCORE

        # 2. Add points for proximity to enemy master (offensive pressure)
        dist_to_enemy = manhattan_distance(
            dest_coords.row_index,
            dest_coords.column_index,
            board_evaluation.enemy_master_coords.row_index,
            board_evaluation.enemy_master_coords.column_index,
        )
        score += (
            MAX_BOARD_DISTANCE - dist_to_enemy
        ) * MOVE_WEIGHT_DISTANCE_TO_ENEMY_MASTER

        # 3. Defensive positioning (if master is threatened)
        if board_evaluation.master_threat_level >= DEFENSIVE_MOVE_THREAT_THRESHOLD:
            dist_to_own = manhattan_distance(
                dest_coords.row_index,
                dest_coords.column_index,
                board_evaluation.ai_master_coords.row_index,
                board_evaluation.ai_master_coords.column_index,
            )
            # Higher score for being closer to own master (blocking/defending)
            score += (
                MAX_BOARD_DISTANCE - dist_to_own
            ) * MOVE_WEIGHT_DISTANCE_TO_OWN_MASTER

        return score
