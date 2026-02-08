import pytest
from ai.strategy.evaluators.cell_evaluator import CellEvaluator
from game_engine.models.dtos.coordinates import Coordinates


class TestCellEvaluatorTarget:
    """Tests for evaluate_target_cell."""

    def test_evaluate_target_cell_is_placeholder(
        self, evaluator: CellEvaluator
    ) -> None:
        """Test that evaluate_target_cell returns 0.0 as it is currently a placeholder."""
        # Arrange
        coords = Coordinates(0, 0)

        # Act
        score = evaluator.evaluate_target_cell(coords)

        # Assert
        assert score == 0.0
