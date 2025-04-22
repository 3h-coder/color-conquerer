import time
from unittest.mock import MagicMock
from tests.helpers.match_helper import MatchHelper


def test_inactive_player_loses_the_match(match: MatchHelper):
    # Arrange
    match.initiate()

    player_kick_delay_in_s = 0.03
    match.match_handler_unit.end = MagicMock(wraps=match.match_handler_unit.end)
    match_end = match.match_handler_unit.end

    match.set_inactivity_delays(0.01, 0.02, player_kick_delay_in_s)

    # Act
    match.start()
    time.sleep(player_kick_delay_in_s)

    # Assert
    match_end.assert_called_once()
