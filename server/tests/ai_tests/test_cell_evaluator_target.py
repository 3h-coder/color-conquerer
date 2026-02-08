import pytest
from unittest.mock import MagicMock
from ai.strategy.evaluators.cell_evaluator import CellEvaluator
from ai.config.ai_config import (
    ATTACK_WEIGHT_BASE_ATTACK,
    ATTACK_WEIGHT_THREAT_DEFENSE,
    ATTACK_WEIGHT_LOW_HP_BONUS,
    ATTACK_WEIGHT_ENEMY_MASTER,
    ATTACK_WEIGHT_LETHAL_ON_MASTER,
)
from game_engine.models.dtos.coordinates import Coordinates
from game_engine.models.cell.cell import Cell


class TestCellEvaluatorTarget:
    """Tests for evaluate_target_cell."""

    def test_evaluate_target_cell_enemy_master(
        self, evaluator: CellEvaluator, board_evaluation: MagicMock
    ) -> None:
        """Test that attacking the enemy master is highly prioritized."""
        # Arrange
        # Enemy master at (9, 5) - defined in conftest.py
        coords = Coordinates(9, 5)
        board_evaluation.ai_has_lethal_opportunity.return_value = False

        # Act
        score = evaluator.evaluate_target_cell(coords, board_evaluation)

        # Assert
        assert score == ATTACK_WEIGHT_ENEMY_MASTER

    def test_evaluate_target_cell_lethal_master(
        self, evaluator: CellEvaluator, board_evaluation: MagicMock
    ) -> None:
        """Test that lethal opportunities on enemy master get a major bonus."""
        # Arrange
        # Enemy master at (9, 5)
        coords = Coordinates(9, 5)
        board_evaluation.ai_has_lethal_opportunity.return_value = True

        # Act
        score = evaluator.evaluate_target_cell(coords, board_evaluation)

        # Assert
        assert score == ATTACK_WEIGHT_ENEMY_MASTER + ATTACK_WEIGHT_LETHAL_ON_MASTER

    def test_evaluate_target_cell_basic_unit(
        self, evaluator: CellEvaluator, board_evaluation: MagicMock
    ) -> None:
        """Test basic attack scoring for regular units."""
        # Arrange
        coords = Coordinates(5, 5)
        board_evaluation.enemy_cells_near_ai_master = []

        target_cell = MagicMock(spec=Cell)
        target_cell.is_shielded.return_value = True

        evaluator._match_context.game_board = MagicMock()
        evaluator._match_context.game_board.get.return_value = target_cell

        # Act
        score = evaluator.evaluate_target_cell(coords, board_evaluation)

        # Assert
        assert score == ATTACK_WEIGHT_BASE_ATTACK

    def test_evaluate_target_cell_threat_defensive(
        self, evaluator: CellEvaluator, board_evaluation: MagicMock
    ) -> None:
        """Test that targets near our own master are prioritized."""
        # Arrange
        coords = Coordinates(2, 5)
        target_cell = MagicMock(spec=Cell)
        target_cell.is_shielded.return_value = True

        board_evaluation.enemy_cells_near_ai_master = [target_cell]
        evaluator._match_context.game_board = MagicMock()
        evaluator._match_context.game_board.get.return_value = target_cell

        # Act
        score = evaluator.evaluate_target_cell(coords, board_evaluation)

        # Assert
        assert score == ATTACK_WEIGHT_BASE_ATTACK + ATTACK_WEIGHT_THREAT_DEFENSE

    def test_evaluate_target_cell_low_hp_clear(
        self, evaluator: CellEvaluator, board_evaluation: MagicMock
    ) -> None:
        """Test that non-shielded targets get a bonus (easier to clear)."""
        # Arrange
        coords = Coordinates(5, 5)
        target_cell = MagicMock(spec=Cell)
        target_cell.is_shielded.return_value = False
        board_evaluation.enemy_cells_near_ai_master = []

        evaluator._match_context.game_board = MagicMock()
        evaluator._match_context.game_board.get.return_value = target_cell

        # Act
        score = evaluator.evaluate_target_cell(coords, board_evaluation)

        # Assert
        assert score == ATTACK_WEIGHT_BASE_ATTACK + ATTACK_WEIGHT_LOW_HP_BONUS
