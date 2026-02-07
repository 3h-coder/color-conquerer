"""
import pytest
from unittest.mock import MagicMock, patch
from ai.strategy.decision_makers.movement_decider import MovementDecider
from game_engine.models.actions.cell_movement import CellMovement
from game_engine.models.dtos.coordinates import Coordinates


class TestMovementDecider:
    @pytest.fixture
    def mock_match(self):
        match = MagicMock()
        match.match_context = MagicMock()
        return match

    @pytest.fixture
    def decider(self, mock_match):
        return MovementDecider(mock_match, ai_is_player1=True)

    @patch(
        "ai.strategy.decision_makers.movement_decider.get_possible_movements_and_attacks"
    )
    def test_decide_movement_picks_closer_to_master(self, mock_get_options, decider):
        \"\"\"Test that the AI prefers movements that get closer to the enemy master.\"\"\"
        # Arrange
        evaluation = MagicMock()
        evaluation.enemy_master_coords = Coordinates(8, 5)

        # Move from (2,5) to (3,5) - gets closer
        move_good = MagicMock(spec=CellMovement)
        move_good.metadata = MagicMock()
        move_good.metadata.originating_coords = Coordinates(2, 5)
        move_good.metadata.impacted_coords = Coordinates(3, 5)

        # Move from (2,5) to (1,5) - moves away
        move_bad = MagicMock(spec=CellMovement)
        move_bad.metadata = MagicMock()
        move_bad.metadata.originating_coords = Coordinates(2, 5)
        move_bad.metadata.impacted_coords = Coordinates(1, 5)

        mock_get_options.return_value = {move_good, move_bad}

        with patch.object(decider, "_get_ai_cells", return_value=[MagicMock()]):
            # Act
            action = decider.decide_movement(evaluation)

            # Assert
            assert action == move_good

    @patch(
        "ai.strategy.decision_makers.movement_decider.get_possible_movements_and_attacks"
    )
    def test_decide_movement_no_options(self, mock_get_options, decider):
        \"\"\"Test that None is returned if no movements are possible.\"\"\"
        # Arrange
        mock_get_options.return_value = set()
        evaluation = MagicMock()

        # Act
        action = decider.decide_movement(evaluation)

        # Assert
        assert action is None
"""
