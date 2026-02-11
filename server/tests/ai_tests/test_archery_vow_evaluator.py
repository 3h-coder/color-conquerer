import pytest
from unittest.mock import MagicMock
from ai.strategy.evaluators.spells.archery_vow_evaluator import ArcheryVowEvaluator
from ai.config.ai_config import SpellWeights, EvaluationConstants
from game_engine.models.dtos.coordinates import Coordinates
from game_engine.models.spells.spell_id import SpellId
from game_engine.models.actions.spell_casting import SpellCasting
from utils.board_utils import manhattan_distance


class TestArcheryVowEvaluator:
    """Tests for ArcheryVowEvaluator."""

    @pytest.fixture
    def evaluator(self, mock_match) -> ArcheryVowEvaluator:
        return ArcheryVowEvaluator(mock_match, ai_is_player1=True)

    @pytest.fixture
    def spell_action(self) -> MagicMock:
        action = MagicMock(spec=SpellCasting)
        action.metadata = MagicMock()
        action.spell = MagicMock()
        action.spell.ID = SpellId.ARCHERY_VOW
        return action

    def test_archery_vow_zero_score_if_already_archer(
        self,
        evaluator: ArcheryVowEvaluator,
        board_evaluation: MagicMock,
        spell_action: MagicMock,
    ) -> None:
        """Test that already archer cells get zero score."""
        # Arrange
        spell_action.metadata.impacted_coords = Coordinates(5, 5)
        target_cell = evaluator._match_context.game_board.board[5][5]
        target_cell.is_archer.return_value = True

        # Act
        score = evaluator.evaluate_spell(spell_action, board_evaluation)

        # Assert
        assert score == 0.0

    def test_archery_vow_score_calculation(
        self,
        evaluator: ArcheryVowEvaluator,
        board_evaluation: MagicMock,
        spell_action: MagicMock,
    ) -> None:
        """Test standard score calculation for Archery Vow."""
        # Arrange
        # Target at (5,5), enemy master at (9,5) per conftest
        target_coords = Coordinates(5, 5)
        spell_action.metadata.impacted_coords = target_coords

        target_cell = evaluator._match_context.game_board.board[5][5]
        target_cell.is_archer.return_value = False

        # Act
        score = evaluator.evaluate_spell(spell_action, board_evaluation)

        # Assert
        dist_to_enemy = manhattan_distance(5, 5, 9, 5)  # 4
        expected_position_bonus = (
            max(0, (EvaluationConstants.MAX_BOARD_DISTANCE - dist_to_enemy) * 0.5)
            + SpellWeights.ARCHERY_VOW_FORWARD_POSITION_BONUS
        )
        expected = (
            SpellWeights.ARCHERY_VOW_BASE
            + SpellWeights.ARCHERY_VOW_AVAILABILITY_BONUS
            + expected_position_bonus
        )
        assert score == expected

    def test_archery_vow_forward_bonus_difference(
        self,
        evaluator: ArcheryVowEvaluator,
        board_evaluation: MagicMock,
        spell_action: MagicMock,
    ) -> None:
        """Test that forward positions score higher than backward positions."""
        # Arrange
        target_cell_forward = evaluator._match_context.game_board.board[8][5]
        target_cell_forward.is_archer.return_value = False

        target_cell_backward = evaluator._match_context.game_board.board[1][5]
        target_cell_backward.is_archer.return_value = False

        # Act
        spell_action.metadata.impacted_coords = Coordinates(8, 5)
        score_forward = evaluator.evaluate_spell(spell_action, board_evaluation)

        spell_action.metadata.impacted_coords = Coordinates(1, 5)
        score_backward = evaluator.evaluate_spell(spell_action, board_evaluation)

        # Assert
        assert score_forward > score_backward
