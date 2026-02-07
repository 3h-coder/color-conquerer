import pytest
from unittest.mock import MagicMock
from ai.strategy.evaluators.cell_evaluator import CellEvaluator
from ai.strategy.evaluators.board.board_evaluation import BoardEvaluation
from ai.strategy.evaluators.board.evaluation_constants import (
    MAX_THREAT_LEVEL,
    MIN_THREAT_LEVEL,
)
from ai.config.ai_config import (
    BASE_SPAWN_SCORE,
    MAX_BOARD_DISTANCE,
    SPAWN_WEIGHT_DISTANCE_TO_ENEMY_MASTER,
)
from game_engine.models.dtos.coordinates import Coordinates
from game_engine.models.match.match_context import MatchContext
from handlers.match_handler_unit import MatchHandlerUnit


class TestCellEvaluator:
    @pytest.fixture
    def mock_match(self) -> MagicMock:
        match = MagicMock(spec=MatchHandlerUnit)
        match.match_context = MagicMock(spec=MatchContext)
        return match

    @pytest.fixture
    def evaluator(self, mock_match: MagicMock) -> CellEvaluator:
        return CellEvaluator(mock_match, ai_is_player1=True)

    @pytest.fixture
    def board_evaluation(self) -> MagicMock:
        # Create a mock board evaluation
        # Player 1 Master at (1, 5)
        # Player 2 Master at (9, 5)
        eval_obj = MagicMock(spec=BoardEvaluation)
        eval_obj.ai_master_coords = Coordinates(1, 5)
        eval_obj.enemy_master_coords = Coordinates(9, 5)
        eval_obj.master_threat_level = MIN_THREAT_LEVEL
        return eval_obj

    def test_evaluate_spawn_location_proximity_to_enemy(
        self, evaluator: CellEvaluator, board_evaluation: MagicMock
    ) -> None:
        """Test that spawns closer to enemy master are scored higher for pressure."""
        # Arrange
        near_coords = Coordinates(8, 5)  # Dist 1 to enemy (9,5)
        far_coords = Coordinates(2, 5)  # Dist 7 to enemy (9,5)

        # Act
        score_near = evaluator.evaluate_spawn_location(near_coords, board_evaluation)
        score_far = evaluator.evaluate_spawn_location(far_coords, board_evaluation)

        # Assert
        assert score_near > score_far

    def test_evaluate_spawn_location_defensive_priority(
        self, evaluator: CellEvaluator, board_evaluation: MagicMock
    ) -> None:
        """Test that under high threat, spawns closer to own master are prioritized."""
        # Arrange
        board_evaluation.master_threat_level = MAX_THREAT_LEVEL  # High threat

        # We pick two points equidistant from the enemy master (9,5)
        # Point A: (2, 5) -> Dist to enemy: 7, Dist to own (1,5): 1
        # Point B: (5, 8) -> Dist to enemy: 4+3=7, Dist to own (1,5): 4+3=7
        near_own = Coordinates(2, 5)
        far_own = Coordinates(5, 8)

        # Act
        score_near = evaluator.evaluate_spawn_location(near_own, board_evaluation)
        score_far = evaluator.evaluate_spawn_location(far_own, board_evaluation)

        # Assert
        assert score_near > score_far

    def test_evaluate_spawn_location_no_defense_when_safe(
        self, evaluator: CellEvaluator, board_evaluation: MagicMock
    ) -> None:
        """Test that when safe (threat=0), distance to own master doesn't significantly boost score."""
        # Arrange
        board_evaluation.master_threat_level = MIN_THREAT_LEVEL

        # We need points with same distance to enemy but different distance to own
        # Enemy (9,5), Own (1,5)
        # Near own: (2, 5) -> Dist to enemy: 7, Dist to own: 1
        # Far from both: (5, 8) -> Dist to enemy: 4+3=7, Dist to own: 4+3=7
        pos_near_own = Coordinates(2, 5)
        pos_equidistant = Coordinates(5, 8)

        # Act
        score_near_own = evaluator.evaluate_spawn_location(
            pos_near_own, board_evaluation
        )
        score_far_away = evaluator.evaluate_spawn_location(
            pos_equidistant, board_evaluation
        )

        # Assert: Since threat is 0, the distance to own master should be ignored.
        # Both should have similar scores because their distance to enemy is the same.
        assert score_near_own == pytest.approx(score_far_away)

    def test_evaluate_spawn_location_at_enemy_master(
        self, evaluator: CellEvaluator, board_evaluation: MagicMock
    ) -> None:
        """Test score when spawning right next to enemy master (theoretical maximum)."""
        # Arrange
        # Enemy master at (9, 5)
        pos = Coordinates(8, 5)  # Distance 1

        # Act
        score = evaluator.evaluate_spawn_location(pos, board_evaluation)

        # Assert
        expected_score = (
            BASE_SPAWN_SCORE
            + (MAX_BOARD_DISTANCE - 1) * SPAWN_WEIGHT_DISTANCE_TO_ENEMY_MASTER
        )
        assert score == expected_score

    def test_evaluate_spawn_location_at_max_distance(
        self, evaluator: CellEvaluator, board_evaluation: MagicMock
    ) -> None:
        """Test score when spawning at maximum possible distance from enemy master."""
        # Arrange
        # Enemy master at (9, 5)
        pos = Coordinates(0, 0)  # Dist to (9,5) is 9+5 = 14.

        # Act
        score = evaluator.evaluate_spawn_location(pos, board_evaluation)

        # Assert
        expected_score = (
            BASE_SPAWN_SCORE
            + (MAX_BOARD_DISTANCE - 14) * SPAWN_WEIGHT_DISTANCE_TO_ENEMY_MASTER
        )
        assert score == expected_score
