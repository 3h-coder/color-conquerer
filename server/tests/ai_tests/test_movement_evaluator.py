import pytest
from unittest.mock import MagicMock
from ai.strategy.evaluators.movement_evaluator import MovementEvaluator
from ai.strategy.evaluators.board.evaluation_constants import (
    MAX_THREAT_LEVEL,
    MIN_THREAT_LEVEL,
)
from ai.config.ai_config import (
    BASE_MOVE_SCORE,
    MOVE_WEIGHT_DISTANCE_TO_ENEMY_MASTER,
    MAX_BOARD_DISTANCE,
)
from game_engine.models.dtos.coordinates import Coordinates


class TestMovementEvaluator:
    """Tests for MovementEvaluator."""

    def test_movement_closer_to_enemy_scores_higher(
        self, movement_evaluator: MovementEvaluator, board_evaluation: MagicMock
    ) -> None:
        """Destination closer to enemy master should score higher."""
        # Arrange
        near = Coordinates(8, 5)  # dist 1 to enemy (9,5)
        far = Coordinates(3, 5)  # dist 6 to enemy (9,5)

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
        pos_a = Coordinates(5, 5)  # dist = |5-9| + |5-5| = 4
        pos_b = Coordinates(7, 3)  # dist = |7-9| + |3-5| = 4

        # Act
        score_a = movement_evaluator.evaluate(pos_a, board_evaluation)
        score_b = movement_evaluator.evaluate(pos_b, board_evaluation)

        # Assert
        assert score_a == pytest.approx(score_b)

    def test_movement_defensive_when_threatened(
        self, movement_evaluator: MovementEvaluator, board_evaluation: MagicMock
    ) -> None:
        """Under high threat, destinations closer to own master should score higher."""
        # Arrange
        board_evaluation.master_threat_level = MAX_THREAT_LEVEL

        # Both equidistant from enemy (9,5) at dist 7
        near_own = Coordinates(2, 5)  # dist to own (1,5) = 1, dist to enemy = 7
        far_own = Coordinates(5, 8)  # dist to own (1,5) = 7, dist to enemy = 7

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
        near_own = Coordinates(2, 5)  # dist to own (1,5) = 1, dist to enemy = 7
        far_own = Coordinates(5, 8)  # dist to own (1,5) = 7, dist to enemy = 7

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
        coords = Coordinates(5, 5)

        # Act
        score1 = movement_evaluator.evaluate(coords, board_evaluation)
        score2 = movement_evaluator.evaluate(coords, board_evaluation)

        # Assert
        assert score1 == score2

    def test_movement_exact_score_at_enemy_master(
        self, movement_evaluator: MovementEvaluator, board_evaluation: MagicMock
    ) -> None:
        """Verify exact score computation for a destination adjacent to the enemy master."""
        # Arrange
        pos = Coordinates(8, 5)  # dist 1 to enemy (9,5)

        # Act
        score = movement_evaluator.evaluate(pos, board_evaluation)

        # Assert
        expected = (
            BASE_MOVE_SCORE
            + (MAX_BOARD_DISTANCE - 1) * MOVE_WEIGHT_DISTANCE_TO_ENEMY_MASTER
        )
        assert score == expected
