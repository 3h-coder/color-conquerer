import pytest
from unittest.mock import MagicMock
from ai.strategy.evaluators.spells.celerity_evaluator import CelerityEvaluator
from ai.config.ai_config import SpellWeights
from game_engine.models.dtos.coordinates import Coordinates
from game_engine.models.spells.spell_id import SpellId
from game_engine.models.actions.spell_casting import SpellCasting


class TestCelerityEvaluator:
    """Tests for CelerityEvaluator."""

    @pytest.fixture
    def evaluator(self, mock_match) -> CelerityEvaluator:
        return CelerityEvaluator(mock_match, ai_is_player1=True)

    @pytest.fixture
    def spell_action(self) -> MagicMock:
        action = MagicMock(spec=SpellCasting)
        action.metadata = MagicMock()
        action.spell = MagicMock()
        action.spell.ID = SpellId.CELERITY
        return action

    def test_celerity_early_game_penalty(
        self,
        evaluator: CelerityEvaluator,
        board_evaluation: MagicMock,
        spell_action: MagicMock,
    ) -> None:
        """Test that celerity gets a very low score in early game."""
        # Arrange
        board_evaluation.current_turn = 2
        target_coords = Coordinates(5, 5)
        spell_action.metadata.impacted_coords = target_coords
        spell_action.spell.get_impacted_cells.return_value = [target_coords]

        # Act
        score = evaluator.evaluate_spell(spell_action, board_evaluation)

        # Assert
        assert score == 2.0

    def test_celerity_base_score_mid_game(
        self,
        evaluator: CelerityEvaluator,
        board_evaluation: MagicMock,
        spell_action: MagicMock,
    ) -> None:
        """Test base score calculation in mid game with no special factors."""
        # Arrange
        board_evaluation.current_turn = 10
        board_evaluation.positional_advantage = 0
        target_coords = Coordinates(5, 5)
        spell_action.metadata.impacted_coords = target_coords
        spell_action.spell.get_impacted_cells.return_value = [target_coords]

        # Mock only target cell as AI owned
        target_cell = evaluator._match_context.game_board.board[5][5]
        target_cell.row_index = 5
        target_cell.column_index = 5
        target_cell.is_archer.return_value = False
        target_cell.is_master = False
        target_cell.is_shielded.return_value = False
        target_cell.is_accelerated.return_value = False

        evaluator._match_context.game_board.get_cells_owned_by_player.return_value = [
            target_cell
        ]

        # Act
        score = evaluator.evaluate_spell(spell_action, board_evaluation)

        # Assert
        # diagonal_cells will only contain target_coords (size 1)
        expected = SpellWeights.CELERITY_BASE + 1 * SpellWeights.CELERITY_PER_CELL_BONUS
        assert score == expected

    def test_celerity_advantage_bonus(
        self,
        evaluator: CelerityEvaluator,
        board_evaluation: MagicMock,
        spell_action: MagicMock,
    ) -> None:
        """Test bonus when having positional advantage."""
        # Arrange
        board_evaluation.current_turn = 10
        board_evaluation.positional_advantage = 10.0
        target_coords = Coordinates(5, 5)
        spell_action.metadata.impacted_coords = target_coords
        spell_action.spell.get_impacted_cells.return_value = [target_coords]

        target_cell = evaluator._match_context.game_board.board[5][5]
        target_cell.row_index = 5
        target_cell.column_index = 5
        target_cell.is_archer.return_value = False
        target_cell.is_master = False
        target_cell.is_shielded.return_value = False
        target_cell.is_accelerated.return_value = False

        evaluator._match_context.game_board.get_cells_owned_by_player.return_value = [
            target_cell
        ]

        # Act
        score = evaluator.evaluate_spell(spell_action, board_evaluation)

        # Assert
        expected = (
            SpellWeights.CELERITY_BASE
            + SpellWeights.CELERITY_ADVANTAGE_BONUS
            + 1 * SpellWeights.CELERITY_PER_CELL_BONUS
        )
        assert score == expected

    def test_celerity_diagonal_and_special_cell_bonus(
        self,
        evaluator: CelerityEvaluator,
        board_evaluation: MagicMock,
        spell_action: MagicMock,
    ) -> None:
        """Test bonus for larger diagonals and special cells."""
        # Arrange
        board_evaluation.current_turn = 10
        board_evaluation.positional_advantage = 0
        target_coords = Coordinates(5, 5)
        spell_action.metadata.impacted_coords = target_coords

        # Create a diagonal of 3 cells
        # (5,5), (4,4), (3,3)
        coords_list = [(5, 5), (4, 4), (3, 3)]
        cells = []
        for r, c in coords_list:
            cell = evaluator._match_context.game_board.board[r][c]
            cell.row_index = r
            cell.column_index = c
            cell.is_archer.return_value = False
            cell.is_master = False
            cell.is_shielded.return_value = False
            cell.is_accelerated.return_value = False
            cells.append(cell)

        # Make one cell special (archer)
        cells[1].is_archer.return_value = True  # (4,4) is an archer

        # Mock the spell formation
        spell_action.spell.get_impacted_cells.return_value = [
            Coordinates(r, c) for r, c in coords_list
        ]

        evaluator._match_context.game_board.get_cells_owned_by_player.return_value = (
            cells
        )

        # Act
        score = evaluator.evaluate_spell(spell_action, board_evaluation)

        # Assert
        expected = (
            SpellWeights.CELERITY_BASE
            + 3 * SpellWeights.CELERITY_PER_CELL_BONUS
            + 1 * SpellWeights.CELERITY_SPECIAL_CELL_BONUS
        )
        assert score == expected

    def test_celerity_redundant_penalty(
        self,
        evaluator: CelerityEvaluator,
        board_evaluation: MagicMock,
        spell_action: MagicMock,
    ) -> None:
        """Test penalty for already accelerated cells."""
        # Arrange
        board_evaluation.current_turn = 10
        board_evaluation.positional_advantage = 0
        target_coords = Coordinates(5, 5)
        spell_action.metadata.impacted_coords = target_coords

        # Create a diagonal of 2 cells
        coords_list = [(5, 5), (4, 4)]
        cells = []
        for r, c in coords_list:
            cell = evaluator._match_context.game_board.board[r][c]
            cell.row_index = r
            cell.column_index = c
            cell.is_archer.return_value = False
            cell.is_master = False
            cell.is_shielded.return_value = False
            cell.is_accelerated.return_value = False
            cells.append(cell)

        # Make one cell already accelerated
        cells[1].is_accelerated.return_value = True

        # Mock the spell formation
        spell_action.spell.get_impacted_cells.return_value = [
            Coordinates(r, c) for r, c in coords_list
        ]

        evaluator._match_context.game_board.get_cells_owned_by_player.return_value = (
            cells
        )

        # Act
        score = evaluator.evaluate_spell(spell_action, board_evaluation)

        # Assert
        expected = (
            SpellWeights.CELERITY_BASE
            + 2 * SpellWeights.CELERITY_PER_CELL_BONUS
            - 1 * SpellWeights.CELERITY_REDUNDANT_PENALTY
        )
        assert score == expected
