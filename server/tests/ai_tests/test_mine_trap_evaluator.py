import pytest
from unittest.mock import MagicMock
from ai.strategy.evaluators.spells.mine_trap_evaluator import MineTrapEvaluator
from ai.config.ai_config import SpellWeights
from game_engine.models.dtos.coordinates import Coordinates
from game_engine.models.spells.spell_id import SpellId
from game_engine.models.actions.spell_casting import SpellCasting
from game_engine.models.cell.cell_owner import CellOwner


class TestMineTrapEvaluator:
    """Tests for MineTrapEvaluator."""

    @pytest.fixture
    def evaluator(self, mock_match) -> MineTrapEvaluator:
        # Initialize board cells with CellOwner.NONE to avoid false-positive enemy neighbor detections
        for row in mock_match.game_board.board:
            for cell in row:
                cell.owner = CellOwner.NONE
        return MineTrapEvaluator(mock_match, ai_is_player1=True)

    @pytest.fixture
    def spell_action(self) -> MagicMock:
        action = MagicMock(spec=SpellCasting)
        action.metadata = MagicMock()
        action.spell = MagicMock()
        action.spell.ID = SpellId.MINE_TRAP
        return action

    def test_mine_trap_early_game_penalty(
        self,
        evaluator: MineTrapEvaluator,
        board_evaluation: MagicMock,
        spell_action: MagicMock,
    ) -> None:
        """Test that mines get a very low score in early game."""
        # Arrange
        board_evaluation.current_turn = 2  # Early game
        spell_action.metadata.impacted_coords = Coordinates(5, 5)

        # Act
        score = evaluator.evaluate_spell(spell_action, board_evaluation)

        # Assert
        assert score == 2.0

    def test_mine_trap_base_score_mid_game(
        self,
        evaluator: MineTrapEvaluator,
        board_evaluation: MagicMock,
        spell_action: MagicMock,
    ) -> None:
        """Test base score calculation far from master and enemies."""
        # Arrange
        board_evaluation.current_turn = 10
        # Far from AI master at (1, 5)
        spell_action.metadata.impacted_coords = Coordinates(8, 5)

        # Act
        score = evaluator.evaluate_spell(spell_action, board_evaluation)

        # Assert
        assert score == SpellWeights.MINE_TRAP_BASE

    def test_mine_trap_proximity_bonus(
        self,
        evaluator: MineTrapEvaluator,
        board_evaluation: MagicMock,
        spell_action: MagicMock,
    ) -> None:
        """Test bonus for being near own master."""
        # Arrange
        board_evaluation.current_turn = 10
        # AI Master is at (1, 5). Target at (2, 5) -> dist 1
        spell_action.metadata.impacted_coords = Coordinates(2, 5)

        # Act
        score = evaluator.evaluate_spell(spell_action, board_evaluation)

        # Assert
        dist = 1
        expected = (
            SpellWeights.MINE_TRAP_BASE
            + (5 - dist) * SpellWeights.MINE_TRAP_OWN_MASTER_PROXIMITY_FACTOR
        )
        assert score == expected

    def test_mine_trap_enemy_neighbor_bonus(
        self,
        evaluator: MineTrapEvaluator,
        board_evaluation: MagicMock,
        spell_action: MagicMock,
    ) -> None:
        """Test bonus for being adjacent to enemy cells."""
        # Arrange
        board_evaluation.current_turn = 10
        target_coords = Coordinates(5, 5)
        spell_action.metadata.impacted_coords = target_coords

        # Add an enemy neighbor (AI is player 1, enemy is player 2)
        enemy_neighbor = evaluator._match_context.game_board.board[6][5]
        enemy_neighbor.owner = CellOwner.PLAYER_2

        # Act
        score = evaluator.evaluate_spell(spell_action, board_evaluation)

        # Assert
        # Dist to master is 4 ( (5,5) to (1,5) )
        prox_bonus = (5 - 4) * SpellWeights.MINE_TRAP_OWN_MASTER_PROXIMITY_FACTOR
        neighbor_bonus = 1 * 2.0
        expected = SpellWeights.MINE_TRAP_BASE + prox_bonus + neighbor_bonus
        assert score == expected

    def test_mine_trap_cluster_bonus(
        self,
        evaluator: MineTrapEvaluator,
        board_evaluation: MagicMock,
        spell_action: MagicMock,
    ) -> None:
        """Test bonus when enemy neighbors belong to a large cluster."""
        # Arrange
        board_evaluation.current_turn = 10
        target_coords = Coordinates(5, 5)
        spell_action.metadata.impacted_coords = target_coords

        # Enemy neighbor
        enemy_neighbor = evaluator._match_context.game_board.board[6][5]
        enemy_neighbor.owner = CellOwner.PLAYER_2

        # Define a cluster containing that neighbor
        enemy_cluster = [enemy_neighbor, MagicMock(), MagicMock()]  # Size 3
        board_evaluation.enemy_cell_clusters = [enemy_cluster]

        # Act
        score = evaluator.evaluate_spell(spell_action, board_evaluation)

        # Assert
        prox_bonus = (5 - 4) * SpellWeights.MINE_TRAP_OWN_MASTER_PROXIMITY_FACTOR
        neighbor_bonus = 1 * 2.0
        expected = (
            SpellWeights.MINE_TRAP_BASE
            + prox_bonus
            + neighbor_bonus
            + SpellWeights.MINE_TRAP_ENEMY_CLUSTER_BONUS
        )
        assert score == expected
