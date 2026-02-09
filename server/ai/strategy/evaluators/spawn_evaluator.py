from typing import TYPE_CHECKING
from game_engine.models.dtos.coordinates import Coordinates
from utils.board_utils import manhattan_distance
from ai.config.ai_config import SpawnWeights, EvaluationConstants
from ai.strategy.evaluators.base_evaluator import BaseEvaluator

if TYPE_CHECKING:
    from ai.strategy.evaluators.board.board_evaluation import BoardEvaluation


class SpawnEvaluator(BaseEvaluator):
    """
    Evaluates potential spawn locations for strategic value.
    """

    def evaluate(
        self,
        coords: Coordinates,
        board_evaluation: "BoardEvaluation",
    ) -> float:
        """
        Calculates a score for a potential spawn location.
        Higher scores indicate better locations.
        """
        score = SpawnWeights.BASE_SCORE

        score += self._evaluate_mana_bubble_bonus(coords)
        score += self._evaluate_offensive_pressure(coords, board_evaluation)
        score += self._evaluate_defensive_positioning(coords, board_evaluation)
        score += self._evaluate_master_critical_defense(coords, board_evaluation)

        return score

    def _evaluate_mana_bubble_bonus(self, coords: Coordinates) -> float:
        """
        Check if spawning directly on a mana bubble - very high priority!
        """
        board = self._match_context.game_board
        spawn_cell = board.get(coords.row_index, coords.column_index)
        if spawn_cell.is_mana_bubble():
            return SpawnWeights.MANA_BUBBLE_BONUS
        return 0.0

    def _evaluate_offensive_pressure(
        self, coords: Coordinates, board_evaluation: "BoardEvaluation"
    ) -> float:
        """
        Distance to enemy master - closer is better for offensive pressure.
        """
        dist_to_enemy_master = manhattan_distance(
            coords.row_index,
            coords.column_index,
            board_evaluation.enemy_master_coords.row_index,
            board_evaluation.enemy_master_coords.column_index,
        )
        return (
            EvaluationConstants.MAX_BOARD_DISTANCE - dist_to_enemy_master
        ) * SpawnWeights.DISTANCE_TO_ENEMY_MASTER

    def _evaluate_defensive_positioning(
        self, coords: Coordinates, board_evaluation: "BoardEvaluation"
    ) -> float:
        """
        Distance to own master - prioritize blocking when threatened.
        """
        if (
            board_evaluation.master_threat_level
            <= EvaluationConstants.DEFENSIVE_SPAWN_THREAT_THRESHOLD
        ):
            return 0.0

        dist_to_own_master = manhattan_distance(
            coords.row_index,
            coords.column_index,
            board_evaluation.ai_master_coords.row_index,
            board_evaluation.ai_master_coords.column_index,
        )
        return (
            EvaluationConstants.MAX_BOARD_DISTANCE - dist_to_own_master
        ) * SpawnWeights.DISTANCE_TO_OWN_MASTER

    def _evaluate_master_critical_defense(
        self, coords: Coordinates, board_evaluation: "BoardEvaluation"
    ) -> float:
        """
        When master health is critical, strongly prioritize spawning adjacent to master for protection.
        """
        if not self._is_ai_master_critical_health():
            return 0.0

        dist_to_own_master = manhattan_distance(
            coords.row_index,
            coords.column_index,
            board_evaluation.ai_master_coords.row_index,
            board_evaluation.ai_master_coords.column_index,
        )
        return (
            EvaluationConstants.MAX_BOARD_DISTANCE - dist_to_own_master
        ) * SpawnWeights.MASTER_DEFENSE_BONUS
