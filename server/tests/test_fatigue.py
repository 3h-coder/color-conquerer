import time
from typing import Callable
from unittest.mock import MagicMock

from constants.game_constants import MAX_STAMINA_VALUE
from game_engine.models.match.match_closure import EndingReason
from tests.helpers.match_helper import MatchHelper


def test_fatigue_decreases_each_turn_from_turn_3(started_match: MatchHelper):
    # Arrange
    player1_client, player2_client = started_match.get_clients()
    player1_resources, player2_resources = started_match.get_both_players_resources()

    # Act
    player1_client.end_turn(wait_for_processing=True)
    player2_client.end_turn(wait_for_processing=True)

    # Assert
    assert player1_resources.current_stamina == MAX_STAMINA_VALUE - 1

    # Act again
    player1_client.end_turn(wait_for_processing=True)

    # Assert again
    assert player2_resources.current_stamina == MAX_STAMINA_VALUE - 1


def test_fatigue_damages_player_when_out_of_stamina(started_match: MatchHelper):
    # Arrange
    player1_client, player2_client = started_match.get_clients()
    player1_resources, player2_resources = started_match.get_both_players_resources()
    player1_match_data, _ = started_match.get_both_player_match_data()

    player1_resources.current_stamina = 1
    player2_resources.current_stamina = 1

    # Act
    player1_client.end_turn(wait_for_processing=True)
    player2_client.end_turn(wait_for_processing=True)  # Stamina loss starts at turn 3

    # Assert
    cumulative_fatigue_damage = player1_match_data.fatigue_damage
    assert cumulative_fatigue_damage == 1
    assert (
        player1_resources.current_hp
        == player1_resources.max_hp - cumulative_fatigue_damage
    )

    # Act again
    player1_client.end_turn(wait_for_processing=True)
    player2_client.end_turn(wait_for_processing=True)

    # Assert again
    cumulative_fatigue_damage += player1_match_data.fatigue_damage
    assert cumulative_fatigue_damage == 3
    assert (
        player1_resources.current_hp
        == player1_resources.max_hp - cumulative_fatigue_damage
    )


def test_fatigue_ends_the_match(started_match: MatchHelper):
    # Arrange
    started_match.match_handler_unit.end = MagicMock(
        wraps=started_match.match_handler_unit.end
    )
    match_end = started_match.match_handler_unit.end

    player1_client, player2_client = started_match.get_clients()
    player1_resources, _ = started_match.get_both_players_resources()

    player1_resources.current_hp = 1
    player1_resources.current_stamina = 1

    # Act
    player1_client.end_turn(wait_for_processing=True)
    player2_client.end_turn(wait_for_processing=True)  # Stamina loss starts at turn 3

    # Assert
    match_end.assert_called_once_with(
        EndingReason.FATIGUE,
        loser_id=started_match.get_current_player().player_id,
    )
