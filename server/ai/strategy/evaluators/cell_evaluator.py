from typing import TYPE_CHECKING
from game_engine.models.dtos.coordinates import Coordinates
from utils.board_utils import manhattan_distance
from ai.config.ai_config import (
    SPAWN_WEIGHT_DISTANCE_TO_ENEMY_MASTER,
    SPAWN_WEIGHT_DISTANCE_TO_OWN_MASTER,
    BASE_SPAWN_SCORE,
    MAX_BOARD_DISTANCE,
    DEFENSIVE_SPAWN_THREAT_THRESHOLD,
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

    def evaluate_target_cell(self, target_coords: Coordinates) -> float:
        """
        Calculates a score for an enemy cell as an attack target.
        Used by AttackDecider.
        """
        # TODO: Implement in later stage
        return 0.0

    def evaluate_movement_destination(self, dest_coords: Coordinates) -> float:
        """
        Calculates a score for a movement destination.
        Used by MovementDecider.
        """
        # TODO: Implement in later stage
        return 0.0
