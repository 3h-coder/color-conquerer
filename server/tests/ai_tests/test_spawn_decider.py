import pytest
from unittest.mock import MagicMock, patch
from ai.strategy.decision_makers.spawn_decider import SpawnDecider
from game_engine.models.actions.cell_spawn import CellSpawn
from game_engine.models.dtos.coordinates import Coordinates
from game_engine.models.match.match_context import MatchContext
from handlers.match_handler_unit import MatchHandlerUnit
from ai.strategy.evaluators.board.board_evaluation import BoardEvaluation
from game_engine.models.player.player import Player
from game_engine.models.player.player_resources import PlayerResources
from game_engine.models.game_board import GameBoard
from game_engine.models.actions.metadata.action_metadata import ActionMedatata


class TestSpawnDecider:
    @pytest.fixture
    def mock_match(self) -> MagicMock:
        match = MagicMock(spec=MatchHandlerUnit)
        match_context = MagicMock(spec=MatchContext)
        match.match_context = match_context

        player1 = MagicMock(spec=Player)
        player1.resources = MagicMock(spec=PlayerResources)
        match_context.player1 = player1

        player2 = MagicMock(spec=Player)
        player2.resources = MagicMock(spec=PlayerResources)
        match_context.player2 = player2

        match_context.game_board = MagicMock(spec=GameBoard)

        player1.resources.current_mp = 10
        player2.resources.current_mp = 10
        return match

    @pytest.fixture
    def decider(self, mock_match: MagicMock) -> SpawnDecider:
        return SpawnDecider(mock_match, ai_is_player1=True)

    def test_decide_spawn_no_mana(
        self, decider: SpawnDecider, mock_match: MagicMock
    ) -> None:
        """Test that AI doesn't spawn if it lacks mana."""
        # Arrange
        mock_match.match_context.player1.resources.current_mp = (
            CellSpawn.DEFAULT_MANA_COST - 1
        )
        evaluation = MagicMock(spec=BoardEvaluation)

        # Act
        action = decider.decide_spawn(evaluation)

        # Assert
        assert action is None

    def test_decide_spawn_high_mana_player2(self, mock_match: MagicMock) -> None:
        """Test that AI uses the correct player's mana when acting as Player 2."""
        # Arrange
        decider_p2 = SpawnDecider(mock_match, ai_is_player1=False)
        # Player 2 has insufficient mana
        mock_match.match_context.player2.resources.current_mp = (
            CellSpawn.DEFAULT_MANA_COST - 1
        )
        # Player 1 has plenty
        mock_match.match_context.player1.resources.current_mp = (
            CellSpawn.DEFAULT_MANA_COST + 10
        )

        evaluation = MagicMock(spec=BoardEvaluation)

        # Act
        action = decider_p2.decide_spawn(evaluation)

        # Assert
        # Should return None because Player 2's mana is checked
        assert action is None

    @patch("ai.strategy.decision_makers.spawn_decider.get_possible_spawns")
    def test_decide_spawn_uses_transient_board(
        self,
        mock_get_possible_spawns: MagicMock,
        decider: SpawnDecider,
        mock_match: MagicMock,
    ) -> None:
        """Test that get_possible_spawns is called with a cloned board."""
        # Arrange
        transient_board = MagicMock(spec=GameBoard)
        mock_match.match_context.game_board.clone_as_transient.return_value = (
            transient_board
        )
        mock_get_possible_spawns.return_value = []
        evaluation = MagicMock(spec=BoardEvaluation)

        # Act
        decider.decide_spawn(evaluation)

        # Assert
        mock_get_possible_spawns.assert_called_once_with(True, transient_board)

    @patch("ai.strategy.decision_makers.spawn_decider.get_possible_spawns")
    def test_decide_spawn_picks_best_score(
        self, mock_get_possible_spawns: MagicMock, decider: SpawnDecider
    ) -> None:
        """Test that the decider chooses relevant spawn based on evaluator scores."""
        # Arrange
        spawn1 = MagicMock(spec=CellSpawn)
        spawn1.metadata = MagicMock(spec=ActionMedatata)
        spawn1.metadata.impacted_coords = Coordinates(2, 5)

        spawn2 = MagicMock(spec=CellSpawn)
        spawn2.metadata = MagicMock(spec=ActionMedatata)
        spawn2.metadata.impacted_coords = Coordinates(3, 5)

        mock_get_possible_spawns.return_value = [spawn1, spawn2]
        evaluation = MagicMock(spec=BoardEvaluation)

        # Mock the evaluator to prefer spawn2
        with patch.object(
            decider._cell_evaluator, "evaluate_spawn_location"
        ) as mock_eval:
            mock_eval.side_effect = lambda coords, _: (
                10.0 if coords == spawn1.metadata.impacted_coords else 20.0
            )

            # Act
            action = decider.decide_spawn(evaluation)

            # Assert
            assert action == spawn2

    @patch("ai.strategy.decision_makers.spawn_decider.get_possible_spawns")
    def test_decide_spawn_returns_none_if_no_options(
        self, mock_get_possible_spawns: MagicMock, decider: SpawnDecider
    ) -> None:
        """Test that None is returned if no spawn locations are available."""
        # Arrange
        mock_get_possible_spawns.return_value = []
        evaluation = MagicMock(spec=BoardEvaluation)

        # Act
        action = decider.decide_spawn(evaluation)

        # Assert
        assert action is None
