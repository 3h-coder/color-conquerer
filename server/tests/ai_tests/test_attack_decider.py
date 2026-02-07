"""
import pytest
from unittest.mock import MagicMock, patch
from ai.strategy.decision_makers.attack_decider import AttackDecider
from ai.strategy.evaluators.board.board_evaluation import BoardEvaluation
from game_engine.models.actions.cell_attack import CellAttack
from game_engine.models.dtos.coordinates import Coordinates
from game_engine.models.match.match_context import MatchContext
from game_engine.models.cell.cell import Cell
from handlers.match_handler_unit import MatchHandlerUnit


class TestAttackDecider:
    @pytest.fixture
    def mock_match(self):
        match = MagicMock(spec=MatchHandlerUnit)
        match.match_context = MagicMock(spec=MatchContext)
        return match

    @pytest.fixture
    def decider(self, mock_match):
        return AttackDecider(mock_match, ai_is_player1=True)

    @patch(
        "ai.strategy.decision_makers.attack_decider.get_possible_movements_and_attacks"
    )
    def test_decide_attack_no_options(self, mock_get_options, decider):
        # Arrange
        mock_get_options.return_value = set()
        evaluation = MagicMock(spec=BoardEvaluation)

        # Act
        action = decider.decide_attack(evaluation)

        # Assert
        assert action is None

    @patch(
        "ai.strategy.decision_makers.attack_decider.get_possible_movements_and_attacks"
    )
    def test_decide_attack_prioritizes_master(
        self, mock_get_options, decider, mock_match
    ):
        # Arrange
        evaluation = MagicMock(spec=BoardEvaluation)
        evaluation.enemy_master_coords = Coordinates(8, 5)
        evaluation.ai_has_lethal_opportunity.return_value = False
        evaluation.enemy_cells_near_ai_master = []

        # Mock game_board.get to return a dummy cell
        dummy_cell = MagicMock(spec=Cell)
        dummy_cell.resources.current_hp = 10
        mock_match.match_context.game_board.get.return_value = dummy_cell

        attack_master = MagicMock(spec=CellAttack)
        attack_master.metadata = MagicMock()
        attack_master.metadata.impacted_coords = Coordinates(8, 5)
        attack_master.metadata.originating_coords = Coordinates(7, 5)

        attack_other = MagicMock(spec=CellAttack)
        attack_other.metadata = MagicMock()
        attack_other.metadata.impacted_coords = Coordinates(4, 5)
        attack_other.metadata.originating_coords = Coordinates(3, 5)

        mock_get_options.return_value = {attack_master, attack_other}

        # Mock _get_ai_cells to return one cell that "has" these attack options
        cell = MagicMock(spec=Cell)
        with patch.object(decider, "_get_ai_cells", return_value=[cell]):
            # Act
            action = decider.decide_attack(evaluation)

            # Assert
            assert action == attack_master

    @patch(
        "ai.strategy.decision_makers.attack_decider.get_possible_movements_and_attacks"
    )
    def test_decide_attack_lethal_bonus(self, mock_get_options, decider):
        # Arrange
        evaluation = MagicMock(spec=BoardEvaluation)
        evaluation.enemy_master_coords = Coordinates(8, 5)
        evaluation.ai_has_lethal_opportunity.return_value = True

        attack_master = MagicMock(spec=CellAttack)
        attack_master.metadata = MagicMock()
        attack_master.metadata.impacted_coords = Coordinates(8, 5)

        mock_get_options.return_value = {attack_master}

        with patch.object(decider, "_get_ai_cells", return_value=[MagicMock(spec=Cell)]):
            with patch.object(
                decider, "_score_attack", return_value=1500.0
            ) as mock_score:
                # Act
                decider.decide_attack(evaluation)

                # Assert
                mock_score.assert_called()
"""
