from unittest.mock import MagicMock, patch
from events.events import Events
from tests.helpers.match_helper import MatchHelper


def test_end_turn_does_nothing_if_player_is_not_current_player(
    started_match: MatchHelper,
):
    # Arrange
    started_match.match_handler_unit.force_turn_swap = MagicMock(
        wraps=started_match.match_handler_unit.force_turn_swap
    )
    force_turn_swap = started_match.match_handler_unit.force_turn_swap

    player1_client, player2_client = started_match.get_clients()

    # Act
    player2_client.end_turn()
    # Assert
    force_turn_swap.assert_not_called()

    # Act again
    player1_client.end_turn()
    # Assert again
    force_turn_swap.assert_called_once()
