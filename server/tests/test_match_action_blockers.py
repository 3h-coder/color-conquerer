from unittest.mock import MagicMock

from events.match_events import OUT_OF_MATCH_LOG_ERROR_MSG
from events.match_events import _logger as match_events_logger
from tests.helpers.match_helper import MatchHelper


def test_match_actions_do_nothing_if_player_not_in_match(match: MatchHelper):
    # Arrange
    match_events_logger.error = MagicMock(wraps=match_events_logger.error)
    logger_error = match_events_logger.error
    player1_client, player2_client = match.get_clients()

    # Act

    # Note : If the player really isn't in a match, they technically should not be
    # able to make the below requests from the client, but it's still good practice
    # to ensure they can't as bypassing or manipulating the client is possible.
    player1_client.end_turn()
    player2_client.end_turn()

    player1_client.concede()
    player2_client.concede()

    player1_client.click_any_cell()
    player2_client.click_any_cell()

    player1_client.click_any_spell()
    player2_client.click_any_spell()

    player1_client.click_spawn_button()
    player2_client.click_spawn_button()

    # Assert
    assert logger_error.call_count == 10
    assert len(logger_error.call_args[0]) == 1
    assert OUT_OF_MATCH_LOG_ERROR_MSG in logger_error.call_args[0][0]


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


def test_cell_click_does_nothing_if_player_is_not_current_player(
    started_match: MatchHelper,
):
    # Arrange
    started_match.match_handler_unit.handle_cell_selection = MagicMock(
        wraps=started_match.match_handler_unit.handle_cell_selection
    )
    handle_cell_selection = started_match.match_handler_unit.handle_cell_selection

    player1_client, player2_client = started_match.get_clients()

    # Act
    player2_client.click_any_cell()

    # Assert
    handle_cell_selection.assert_not_called()

    # Act again
    player1_client.click_any_cell()

    # Assert again
    handle_cell_selection.assert_called_once()


def test_spawn_button_does_nothing_if_player_is_not_current_player(
    started_match: MatchHelper,
):
    # Arrange
    started_match.match_handler_unit.handle_spawn_button = MagicMock(
        wraps=started_match.match_handler_unit.handle_spawn_button
    )
    handle_spawn_button = started_match.match_handler_unit.handle_spawn_button

    player1_client, player2_client = started_match.get_clients()

    # Act
    player2_client.click_spawn_button()

    # Assert
    handle_spawn_button.assert_not_called()

    # Act again
    player1_client.click_spawn_button()

    # Assert again
    handle_spawn_button.assert_called_once()


def test_spell_button_does_nothing_if_player_is_not_current_player(
    started_match: MatchHelper,
):
    # Arrange
    started_match.match_handler_unit.handle_spell_button = MagicMock(
        wraps=started_match.match_handler_unit.handle_spell_button
    )
    handle_spell_button = started_match.match_handler_unit.handle_spell_button

    player1_client, player2_client = started_match.get_clients()

    # Act
    player2_client.click_any_spell()

    # Assert
    handle_spell_button.assert_not_called()

    # Act again
    player1_client.click_any_spell()

    # Assert again
    handle_spell_button.assert_called_once()
