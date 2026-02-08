import pytest
from unittest.mock import MagicMock
from ai.strategy.evaluators.attack_evaluator import AttackEvaluator
from ai.config.ai_config import (
    ATTACK_WEIGHT_BASE_ATTACK,
    ATTACK_WEIGHT_THREAT_DEFENSE,
    ATTACK_WEIGHT_LOW_HP_BONUS,
    ATTACK_WEIGHT_ENEMY_MASTER,
    ATTACK_WEIGHT_LETHAL_ON_MASTER,
)
from game_engine.models.dtos.coordinates import Coordinates
from game_engine.models.cell.cell import Cell


class TestAttackEvaluator:
    """Tests for AttackEvaluator."""

    def test_evaluate_enemy_master(
        self, attack_evaluator: AttackEvaluator, board_evaluation: MagicMock
    ) -> None:
        """Test that attacking the enemy master is highly prioritized."""
        # Arrange
        # Enemy master at (9, 5) - defined in conftest.py
        coords = Coordinates(9, 5)
        board_evaluation.ai_has_lethal_opportunity.return_value = False

        # Act
        score = attack_evaluator.evaluate(coords, board_evaluation)

        # Assert
        assert score == ATTACK_WEIGHT_ENEMY_MASTER

    def test_evaluate_lethal_master(
        self, attack_evaluator: AttackEvaluator, board_evaluation: MagicMock
    ) -> None:
        """Test that lethal opportunities on enemy master get a major bonus."""
        # Arrange
        # Enemy master at (9, 5)
        coords = Coordinates(9, 5)
        board_evaluation.ai_has_lethal_opportunity.return_value = True

        # Act
        score = attack_evaluator.evaluate(coords, board_evaluation)

        # Assert
        assert score == ATTACK_WEIGHT_ENEMY_MASTER + ATTACK_WEIGHT_LETHAL_ON_MASTER

    def test_evaluate_basic_unit(
        self, attack_evaluator: AttackEvaluator, board_evaluation: MagicMock
    ) -> None:
        """Test basic attack scoring for regular units."""
        # Arrange
        coords = Coordinates(5, 5)
        board_evaluation.enemy_cells_near_ai_master = []

        target_cell = MagicMock(spec=Cell)
        target_cell.is_shielded.return_value = True
        target_cell.is_archer.return_value = False

        attack_evaluator._match_context.game_board = MagicMock()
        attack_evaluator._match_context.game_board.get.return_value = target_cell

        # Act
        score = attack_evaluator.evaluate(coords, board_evaluation)

        # Assert
        assert score == ATTACK_WEIGHT_BASE_ATTACK

    def test_evaluate_threat_defensive(
        self, attack_evaluator: AttackEvaluator, board_evaluation: MagicMock
    ) -> None:
        """Test that targets near our own master are prioritized."""
        # Arrange
        coords = Coordinates(2, 5)
        target_cell = MagicMock(spec=Cell)
        target_cell.is_shielded.return_value = True
        target_cell.is_archer.return_value = False

        board_evaluation.enemy_cells_near_ai_master = [target_cell]
        attack_evaluator._match_context.game_board = MagicMock()
        attack_evaluator._match_context.game_board.get.return_value = target_cell

        # Act
        score = attack_evaluator.evaluate(coords, board_evaluation)

        # Assert
        assert score == ATTACK_WEIGHT_BASE_ATTACK + ATTACK_WEIGHT_THREAT_DEFENSE

    def test_evaluate_low_hp_clear(
        self, attack_evaluator: AttackEvaluator, board_evaluation: MagicMock
    ) -> None:
        """Test that non-shielded targets get a bonus (easier to clear)."""
        # Arrange
        coords = Coordinates(5, 5)
        target_cell = MagicMock(spec=Cell)
        target_cell.is_shielded.return_value = False
        target_cell.is_archer.return_value = False
        board_evaluation.enemy_cells_near_ai_master = []

        attack_evaluator._match_context.game_board = MagicMock()
        attack_evaluator._match_context.game_board.get.return_value = target_cell

        # Act
        score = attack_evaluator.evaluate(coords, board_evaluation)

        # Assert
        assert score == ATTACK_WEIGHT_BASE_ATTACK + ATTACK_WEIGHT_LOW_HP_BONUS
