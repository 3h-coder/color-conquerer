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
        """Test base score for Shield Formation (Base + 1 non-shielded cell)."""
        # Arrange
        board_evaluation.ai_master_in_critical_danger.return_value = False
        board_evaluation.ai_is_losing.return_value = False
        target_coords = Coordinates(5, 5)
        spell_action.metadata.impacted_coords = target_coords
        spell_action.spell.get_impacted_cells.return_value = [target_coords]

        target_cell = evaluator._match_context.game_board.board[5][5]
        target_cell.is_shielded.return_value = False
        target_cell.belongs_to.return_value = True

        # Act
        score = evaluator.evaluate_spell(spell_action, board_evaluation)

        # Assert
        expected = (
            SpellWeights.SHIELD_FORMATION_BASE
            + SpellWeights.SHIELD_FORMATION_PER_CELL_BONUS
        )
        assert score == expected

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
        target_coords = Coordinates(5, 5)
        spell_action.metadata.impacted_coords = target_coords
        spell_action.spell.get_impacted_cells.return_value = [target_coords]

        target_cell = evaluator._match_context.game_board.board[5][5]
        target_cell.is_shielded.return_value = False
        target_cell.belongs_to.return_value = True

        # Act
        score = evaluator.evaluate_spell(spell_action, board_evaluation)

        # Assert
        expected = (
            SpellWeights.SHIELD_FORMATION_BASE
            + SpellWeights.SHIELD_FORMATION_CRITICAL_BONUS
            + SpellWeights.SHIELD_FORMATION_PER_CELL_BONUS
        )
        assert score == expected

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
        target_coords = Coordinates(5, 5)
        spell_action.metadata.impacted_coords = target_coords
        spell_action.spell.get_impacted_cells.return_value = [target_coords]

        target_cell = evaluator._match_context.game_board.board[5][5]
        target_cell.is_shielded.return_value = False
        target_cell.belongs_to.return_value = True

        # Act
        score = evaluator.evaluate_spell(spell_action, board_evaluation)

        # Assert
        expected = (
            SpellWeights.SHIELD_FORMATION_BASE
            + SpellWeights.SHIELD_FORMATION_CRITICAL_BONUS
            + SpellWeights.SHIELD_FORMATION_PER_CELL_BONUS
        )
        assert score == expected

    def test_shield_formation_redundant_penalty(
        self,
        evaluator: ShieldFormationEvaluator,
        board_evaluation: MagicMock,
        spell_action: MagicMock,
    ) -> None:
        """Test penalty for already shielded friendly cells (1 shielded, 3 non-shielded)."""
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
        # Mock the spell formation using the new clean API
        spell_action.metadata.impacted_coords = Coordinates(5, 5)
        spell_action.spell.get_impacted_cells.return_value = coords

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
            + 3 * SpellWeights.SHIELD_FORMATION_PER_CELL_BONUS
            - 1 * SpellWeights.SHIELD_FORMATION_REDUNDANT_PENALTY
        )
        assert score == expected

    def test_shield_formation_3x3_vs_2x2(
        self,
        evaluator: ShieldFormationEvaluator,
        board_evaluation: MagicMock,
        spell_action: MagicMock,
    ) -> None:
        """Test that a 3x3 square scores much higher than a 2x2 square."""
        # Arrange
        board_evaluation.ai_master_in_critical_danger.return_value = False
        board_evaluation.ai_is_losing.return_value = False

        # 2x2 square of non-shielded AI cells
        coords_2x2 = [Coordinates(r, c) for r in range(5, 7) for c in range(5, 7)]
        for c in coords_2x2:
            cell = evaluator._match_context.game_board.board[c.row_index][
                c.column_index
            ]
            cell.is_shielded.return_value = False
            cell.belongs_to.return_value = True

        spell_action.metadata.impacted_coords = Coordinates(5, 5)
        spell_action.spell.get_impacted_cells.return_value = coords_2x2
        score_2x2 = evaluator.evaluate_spell(spell_action, board_evaluation)

        # 3x3 square of non-shielded AI cells
        coords_3x3 = [Coordinates(r, c) for r in range(5, 8) for c in range(5, 8)]
        for c in coords_3x3:
            cell = evaluator._match_context.game_board.board[c.row_index][
                c.column_index
            ]
            cell.is_shielded.return_value = False
            cell.belongs_to.return_value = True

        spell_action.metadata.impacted_coords = Coordinates(5, 5)
        spell_action.spell.get_impacted_cells.return_value = coords_3x3
        score_3x3 = evaluator.evaluate_spell(spell_action, board_evaluation)

        # Assert
        assert score_3x3 > score_2x2
        assert (
            score_3x3 - score_2x2 == 5 * SpellWeights.SHIELD_FORMATION_PER_CELL_BONUS
        )  # 9 cells vs 4 cells

    def test_shield_formation_clamping(
        self,
        evaluator: ShieldFormationEvaluator,
        board_evaluation: MagicMock,
        spell_action: MagicMock,
    ) -> None:
        """Test that the score is clamped (not negative and not excessive)."""
        # Arrange
        board_evaluation.ai_master_in_critical_danger.return_value = False
        board_evaluation.ai_is_losing.return_value = False

        # Case 1: All cells already shielded
        coords = [Coordinates(5, 5) for _ in range(10)]
        for c in coords:
            cell = evaluator._match_context.game_board.board[c.row_index][
                c.column_index
            ]
            cell.is_shielded.return_value = True
            cell.belongs_to.return_value = True

        spell_action.metadata.impacted_coords = Coordinates(5, 5)
        spell_action.spell.get_impacted_cells.return_value = coords

        score_low = evaluator.evaluate_spell(spell_action, board_evaluation)
        assert score_low == 0.0

        # Case 2: Max possible score (3x3 non-shielded + critical bonus)
        board_evaluation.ai_master_in_critical_danger.return_value = True
        coords_3x3 = [Coordinates(r, c) for r in range(5, 8) for c in range(5, 8)]
        for c in coords_3x3:
            cell = evaluator._match_context.game_board.board[c.row_index][
                c.column_index
            ]
            cell.is_shielded.return_value = False
            cell.belongs_to.return_value = True

        spell_action.metadata.impacted_coords = Coordinates(5, 5)
        spell_action.spell.get_impacted_cells.return_value = coords_3x3

        score_high = evaluator.evaluate_spell(spell_action, board_evaluation)
        # 85 (base) + 30 (critical) + 90 (9 cells) = 205 -> Clamped to 190
        assert score_high == 190.0
