import pytest
from unittest.mock import MagicMock
from ai.strategy.evaluators.movement_evaluator import MovementEvaluator
from ai.strategy.evaluators.board.evaluation_constants import (
    MAX_THREAT_LEVEL,
    MIN_THREAT_LEVEL,
)
from ai.config.ai_config import (
    MovementWeights,
    EvaluationConstants,
)
from game_engine.models.dtos.coordinates import Coordinates
from game_engine.models.actions.cell_movement import CellMovement


class TestMovementEvaluator:
    """Tests for MovementEvaluator."""

    def _make_movement(self, source: Coordinates, dest: Coordinates) -> MagicMock:
        """Helper to create a mock CellMovement."""
        move = MagicMock(spec=CellMovement)
        move.metadata = MagicMock()
        move.metadata.originating_coords = source
        move.metadata.impacted_coords = dest
        return move

    def test_movement_closer_to_enemy_scores_higher(
        self, movement_evaluator: MovementEvaluator, board_evaluation: MagicMock
    ) -> None:
        """Destination closer to enemy master should score higher."""
        # Arrange
        near = self._make_movement(
            Coordinates(7, 5), Coordinates(8, 5)
        )  # dist 1 to enemy
        far = self._make_movement(
            Coordinates(4, 5), Coordinates(3, 5)
        )  # dist 6 to enemy

        # Act
        score_near = movement_evaluator.evaluate(near, board_evaluation)
        score_far = movement_evaluator.evaluate(far, board_evaluation)

        # Assert
        assert score_near > score_far

    def test_movement_equidistant_scores_equal_when_safe(
        self, movement_evaluator: MovementEvaluator, board_evaluation: MagicMock
    ) -> None:
        """Two destinations at equal distance from enemy master should score the same when not threatened."""
        # Arrange
        # Both dist 4 from enemy at (9,5)
        move_a = self._make_movement(Coordinates(4, 5), Coordinates(5, 5))  # dist 4
        move_b = self._make_movement(Coordinates(6, 3), Coordinates(7, 3))  # dist 4

        # Act
        score_a = movement_evaluator.evaluate(move_a, board_evaluation)
        score_b = movement_evaluator.evaluate(move_b, board_evaluation)

        # Assert
        assert score_a == pytest.approx(score_b)

    def test_movement_defensive_when_threatened(
        self, movement_evaluator: MovementEvaluator, board_evaluation: MagicMock
    ) -> None:
        """Under high threat, destinations closer to own master should score higher."""
        # Arrange
        board_evaluation.master_threat_level = MAX_THREAT_LEVEL

        # Both equidistant from enemy (9,5) at dist 7
        near_own = self._make_movement(
            Coordinates(1, 5), Coordinates(2, 5)
        )  # dist to own = 1
        far_own = self._make_movement(
            Coordinates(4, 8), Coordinates(5, 8)
        )  # dist to own = 7

        # Act
        score_near = movement_evaluator.evaluate(near_own, board_evaluation)
        score_far = movement_evaluator.evaluate(far_own, board_evaluation)

        # Assert
        assert score_near > score_far

    def test_movement_no_defensive_bonus_when_safe(
        self, movement_evaluator: MovementEvaluator, board_evaluation: MagicMock
    ) -> None:
        """When threat is below threshold, distance to own master should not affect score."""
        # Arrange
        board_evaluation.master_threat_level = MIN_THREAT_LEVEL

        # Same enemy distance, different own-master distance
        near_own = self._make_movement(
            Coordinates(1, 5), Coordinates(2, 5)
        )  # dist to own = 1
        far_own = self._make_movement(
            Coordinates(4, 8), Coordinates(5, 8)
        )  # dist to own = 7

        # Act
        score_near = movement_evaluator.evaluate(near_own, board_evaluation)
        score_far = movement_evaluator.evaluate(far_own, board_evaluation)

        # Assert
        assert score_near == pytest.approx(score_far)

    def test_movement_score_is_deterministic(
        self, movement_evaluator: MovementEvaluator, board_evaluation: MagicMock
    ) -> None:
        """Same input should always produce the same score."""
        # Arrange
        move = self._make_movement(Coordinates(4, 5), Coordinates(5, 5))

        # Act
        score1 = movement_evaluator.evaluate(move, board_evaluation)
        score2 = movement_evaluator.evaluate(move, board_evaluation)

        # Assert
        assert score1 == score2

    def test_movement_exact_score_at_enemy_master(
        self, movement_evaluator: MovementEvaluator, board_evaluation: MagicMock
    ) -> None:
        """Verify exact score computation for a destination adjacent to the enemy master."""
        # Arrange
        move = self._make_movement(
            Coordinates(7, 5), Coordinates(8, 5)
        )  # dist 1 to enemy

        # Act
        score = movement_evaluator.evaluate(move, board_evaluation)

        # Assert
        expected = (
            MovementWeights.BASE_SCORE
            + (EvaluationConstants.MAX_BOARD_DISTANCE - 1)
            * MovementWeights.DISTANCE_TO_ENEMY_MASTER
        )
        assert score == expected
