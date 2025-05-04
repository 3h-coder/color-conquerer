import time
from unittest.mock import MagicMock

from game_engine.models.match.match_closure import EndingReason
from tests.helpers.match_helper import MatchHelper
from utils.perf_utils import wait_until


def test_player_exit_causes_match_end(match: MatchHelper):
    # Arrange
    match.initiate()

    player1_client, _ = match.get_clients()
    exit_delay_in_s = 0.03
    match.match_handler_unit.end = MagicMock(wraps=match.match_handler_unit.end)
    match_end = match.match_handler_unit.end

    match.set_exit_delay(exit_delay_in_s)

    # Act
    match.start()

    player1_client.disconnect()
    wait_until(lambda: match_end.called, timeout_in_s=exit_delay_in_s + 0.01)

    # Assert
    match_end.assert_called_once_with(
        EndingReason.PLAYER_LEFT,
        loser_id=match.get_current_player().player_id,
    )


def test_player_exit_and_comeback_does_not_end_match(match: MatchHelper):
    # Arrange
    match.initiate()

    player1_client, _ = match.get_clients()
    exit_delay_in_s = 0.1
    match.match_handler_unit.end = MagicMock(wraps=match.match_handler_unit.end)
    match_end = match.match_handler_unit.end

    match.set_exit_delay(exit_delay_in_s)

    # Act
    match.start()

    player1_client.disconnect()
    time.sleep(exit_delay_in_s / 2)
    player1_client.connect()
    time.sleep(exit_delay_in_s / 2 + 0.01)

    # Assert
    match_end.assert_not_called()
