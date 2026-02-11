import pytest
from unittest.mock import MagicMock
from ai.strategy.evaluators.spells.ambush_evaluator import AmbushEvaluator
from ai.config.ai_config import SpellWeights
from game_engine.models.dtos.coordinates import Coordinates
from game_engine.models.spells.spell_id import SpellId
from game_engine.models.actions.spell_casting import SpellCasting
from constants.game_constants import PLAYER_2_ROWS, PLAYER_1_ROWS


class TestAmbushEvaluator:
    """Tests for AmbushEvaluator."""

    @pytest.fixture
    def evaluator(self, mock_match) -> AmbushEvaluator:
        return AmbushEvaluator(mock_match, ai_is_player1=True)

    @pytest.fixture
    def spell_action(self) -> MagicMock:
        action = MagicMock(spec=SpellCasting)
        action.metadata = MagicMock()
        action.spell = MagicMock()
        action.spell.ID = SpellId.AMBUSH
        return action

    def test_ambush_base_score(
        self,
        evaluator: AmbushEvaluator,
        board_evaluation: MagicMock,
        spell_action: MagicMock,
    ) -> None:
        """Test base score for Ambush."""
        # Arrange: Target own side, mid-game (no extra spawn), not an archer
        spell_action.metadata.impacted_coords = Coordinates(PLAYER_1_ROWS[0], 5)
        board_evaluation.current_turn = 10

        target_cell = evaluator._match_context.game_board.board[PLAYER_1_ROWS[0]][5]
        target_cell.is_archer.return_value = False

        # Act
        score = evaluator.evaluate_spell(spell_action, board_evaluation)

        # Assert
        assert score == SpellWeights.AMBUSH_BASE

    def test_ambush_early_game_opponent_side_bonus(
        self,
        evaluator: AmbushEvaluator,
        board_evaluation: MagicMock,
        spell_action: MagicMock,
    ) -> None:
        """Test bonus for ambushing on opponent side early in the game."""
        # Arrange
        board_evaluation.current_turn = 2  # Early game
        spell_action.metadata.impacted_coords = Coordinates(PLAYER_2_ROWS[0], 5)

        target_cell = evaluator._match_context.game_board.board[PLAYER_2_ROWS[0]][5]
        target_cell.is_archer.return_value = False

        # Act
        score = evaluator.evaluate_spell(spell_action, board_evaluation)

        # Assert
        assert score == SpellWeights.AMBUSH_BASE + SpellWeights.AMBUSH_EXTRA_SPAWN_BONUS

    def test_ambush_archer_target_bonus(
        self,
        evaluator: AmbushEvaluator,
        board_evaluation: MagicMock,
        spell_action: MagicMock,
    ) -> None:
        """Test bonus for targeting an archer with no friendly neighbors."""
        # Arrange
        spell_action.metadata.impacted_coords = Coordinates(5, 5)
        target_cell = evaluator._match_context.game_board.board[5][5]
        target_cell.is_archer.return_value = True

        # Mock board to return no friendly neighbors
        evaluator._match_context.game_board.get_neighbours.return_value = []

        # Act
        score = evaluator.evaluate_spell(spell_action, board_evaluation)

        # Assert
        assert (
            score == SpellWeights.AMBUSH_BASE + SpellWeights.AMBUSH_ARCHER_TARGET_BONUS
        )

    def test_ambush_no_archer_bonus_when_friendly_nearby(
        self,
        evaluator: AmbushEvaluator,
        board_evaluation: MagicMock,
        spell_action: MagicMock,
    ) -> None:
        """Test that archer bonus is NOT applied if friendly units are already nearby."""
        # Arrange
        spell_action.metadata.impacted_coords = Coordinates(5, 5)
        target_cell = evaluator._match_context.game_board.board[5][5]
        target_cell.is_archer.return_value = True

        # Mock a friendly neighbor
        friendly_neighbor = MagicMock()
        friendly_neighbor.is_owned.return_value = True
        friendly_neighbor.belongs_to.return_value = True  # AI is player 1
        evaluator._match_context.game_board.get_neighbours.return_value = [
            friendly_neighbor
        ]

        # Act
        score = evaluator.evaluate_spell(spell_action, board_evaluation)

        # Assert
        assert score == SpellWeights.AMBUSH_BASE

    def test_ambush_archer_target_critical_bonus(
        self,
        evaluator: AmbushEvaluator,
        board_evaluation: MagicMock,
        spell_action: MagicMock,
    ) -> None:
        """Test extra bonus for targeting archer when master is at critical health."""
        # Arrange
        spell_action.metadata.impacted_coords = Coordinates(5, 5)
        target_cell = evaluator._match_context.game_board.board[5][5]
        target_cell.is_archer.return_value = True
        evaluator._match_context.game_board.get_neighbours.return_value = []

        # Set AI master to critical health
        evaluator._match_context.player1.resources.current_hp = 2

        # Act
        score = evaluator.evaluate_spell(spell_action, board_evaluation)

        # Assert
        expected = (
            SpellWeights.AMBUSH_BASE
            + SpellWeights.AMBUSH_ARCHER_TARGET_BONUS
            + SpellWeights.AMBUSH_CRITICAL_HEALTH_BONUS
        )
        assert score == expected

    def test_ambush_enemy_master_bonus(
        self,
        evaluator: AmbushEvaluator,
        board_evaluation: MagicMock,
        spell_action: MagicMock,
    ) -> None:
        """Test massive bonus for targeting enemy master when extra spawn is available."""
        # Arrange
        board_evaluation.current_turn = 2  # Early game
        # Enemy master is at (9, 5) per board_evaluation fixture in conftest
        target_coords = Coordinates(9, 5)
        spell_action.metadata.impacted_coords = target_coords

        target_cell = evaluator._match_context.game_board.board[9][5]
        target_cell.is_archer.return_value = False

        # Act
        score = evaluator.evaluate_spell(spell_action, board_evaluation)

        # Assert
        expected = (
            SpellWeights.AMBUSH_BASE
            + SpellWeights.AMBUSH_EXTRA_SPAWN_BONUS
            + SpellWeights.AMBUSH_MASTER_TARGET_BONUS
        )
        assert score == expected
