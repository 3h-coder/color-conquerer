from tests.helpers.match_helper import MatchHelper


def test_end_turn_does_nothing_if_player_is_not_current_player(match: MatchHelper):
    match.start()

    player1_client, player2_client = match.get_clients()

    player2_client.end_turn()
    match.wait_for_turn_swap_completion()

    assert match.get_current_turn() == 1

    player1_client.end_turn()
    match.wait_for_turn_swap_completion()

    assert match.get_current_turn() == 2
