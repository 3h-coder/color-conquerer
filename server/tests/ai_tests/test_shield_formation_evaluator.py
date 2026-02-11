import pytest
from unittest.mock import MagicMock
from ai.strategy.evaluators.spells.shield_formation_evaluator import (
    ShieldFormationEvaluator,
)
from ai.config.ai_config import SpellWeights
from game_engine.models.dtos.coordinates import Coordinates
from game_engine.models.spells.spell_id import SpellId
from game_engine.models.actions.spell_casting import SpellCasting


class TestShieldFormationEvaluator:
    """Tests for ShieldFormationEvaluator."""

    @pytest.fixture
    def evaluator(self, mock_match) -> ShieldFormationEvaluator:
        return ShieldFormationEvaluator(mock_match, ai_is_player1=True)

    @pytest.fixture
    def spell_action(self) -> MagicMock:
        action = MagicMock(spec=SpellCasting)
        action.metadata = MagicMock()
        action.spell = MagicMock()
        action.spell.ID = SpellId.SHIELD_FORMATION
        action.metadata.impacted_coords = []
        return action

    def test_shield_formation_base_score(
        self,
        evaluator: ShieldFormationEvaluator,
        board_evaluation: MagicMock,
        spell_action: MagicMock,
    ) -> None:
        """Test base score for Shield Formation."""
        # Arrange
        board_evaluation.ai_master_in_critical_danger.return_value = False
        board_evaluation.ai_is_losing.return_value = False
        spell_action.metadata.impacted_coords = [Coordinates(5, 5)]

        target_cell = evaluator._match_context.game_board.board[5][5]
        target_cell.is_shielded.return_value = False

        # Act
        score = evaluator.evaluate_spell(spell_action, board_evaluation)

        # Assert
        assert score == SpellWeights.SHIELD_FORMATION_BASE

    def test_shield_formation_critical_bonus(
        self,
        evaluator: ShieldFormationEvaluator,
        board_evaluation: MagicMock,
        spell_action: MagicMock,
    ) -> None:
        """Test bonus when AI master is in critical danger."""
        # Arrange
        board_evaluation.ai_master_in_critical_danger.return_value = True
        board_evaluation.ai_is_losing.return_value = False
        spell_action.metadata.impacted_coords = [Coordinates(5, 5)]

        target_cell = evaluator._match_context.game_board.board[5][5]
        target_cell.is_shielded.return_value = False

        # Act
        score = evaluator.evaluate_spell(spell_action, board_evaluation)

        # Assert
        assert (
            score
            == SpellWeights.SHIELD_FORMATION_BASE
            + SpellWeights.SHIELD_FORMATION_CRITICAL_BONUS
        )

    def test_shield_formation_losing_bonus(
        self,
        evaluator: ShieldFormationEvaluator,
        board_evaluation: MagicMock,
        spell_action: MagicMock,
    ) -> None:
        """Test bonus when AI is losing."""
        # Arrange
        board_evaluation.ai_master_in_critical_danger.return_value = False
        board_evaluation.ai_is_losing.return_value = True
        spell_action.metadata.impacted_coords = [Coordinates(5, 5)]

        target_cell = evaluator._match_context.game_board.board[5][5]
        target_cell.is_shielded.return_value = False

        # Act
        score = evaluator.evaluate_spell(spell_action, board_evaluation)

        # Assert
        assert (
            score
            == SpellWeights.SHIELD_FORMATION_BASE
            + SpellWeights.SHIELD_FORMATION_CRITICAL_BONUS
        )

    def test_shield_formation_redundant_penalty(
        self,
        evaluator: ShieldFormationEvaluator,
        board_evaluation: MagicMock,
        spell_action: MagicMock,
    ) -> None:
        """Test penalty for already shielded friendly cells."""
        # Arrange
        board_evaluation.ai_master_in_critical_danger.return_value = False
        board_evaluation.ai_is_losing.return_value = False

        # 2x2 square
        coords = [
            Coordinates(5, 5),
            Coordinates(5, 6),
            Coordinates(6, 5),
            Coordinates(6, 6),
        ]
        spell_action.metadata.impacted_coords = coords

        # Mock cells
        for c in coords:
            cell = evaluator._match_context.game_board.board[c.row_index][
                c.column_index
            ]
            cell.is_shielded.return_value = False
            cell.belongs_to.return_value = True  # AI owned

        # One cell is already shielded
        evaluator._match_context.game_board.board[5][5].is_shielded.return_value = True

        # Act
        score = evaluator.evaluate_spell(spell_action, board_evaluation)

        # Assert
        expected = (
            SpellWeights.SHIELD_FORMATION_BASE
            - SpellWeights.SHIELD_FORMATION_REDUNDANT_PENALTY
        )
        assert score == expected
