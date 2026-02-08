from typing import TYPE_CHECKING
from game_engine.models.dtos.coordinates import Coordinates
from utils.board_utils import manhattan_distance
from ai.config.ai_config import (
    MOVE_WEIGHT_DISTANCE_TO_ENEMY_MASTER,
    MOVE_WEIGHT_DISTANCE_TO_OWN_MASTER,
    BASE_MOVE_SCORE,
    MAX_BOARD_DISTANCE,
    DEFENSIVE_MOVE_THREAT_THRESHOLD,
)
from ai.strategy.evaluators.base_evaluator import BaseEvaluator

if TYPE_CHECKING:
    from ai.strategy.evaluators.board.board_evaluation import BoardEvaluation


class MovementEvaluator(BaseEvaluator):
    """
    Evaluates potential movement destinations for strategic value.
    """

    def evaluate(
        self,
        dest_coords: Coordinates,
        board_evaluation: "BoardEvaluation",
    ) -> float:
        """
        Calculates a score for a movement destination.
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
