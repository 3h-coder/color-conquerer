from constants.game_constants import (
    STATES_TO_CLEAR_AT_TURN_BEGINNING,
    STATES_TO_CLEAR_AT_TURN_END,
)
from game_engine.models.dtos.match_closure import EndingReason
from game_engine.models.dtos.match_context import MatchContext
from game_engine.models.player.player import Player


def process_turn_change(match_context: MatchContext):
    """
    Enforces a turn change within the match, processing the necessary game logic.

    If the match should end, it returns the reason for the match ending. Otherwise, it returns None.
    """
    # Actual turn change
    match_context.current_turn += 1
    match_context.is_player1_turn = not match_context.is_player1_turn

    match_ending_reason = _post_change_processing(match_context)
    if match_ending_reason:
        return match_ending_reason


def _post_change_processing(match_context: MatchContext):
    """All the processing that needs to be done after the turn change."""
    current_turn = match_context.current_turn
    player = match_context.get_current_player()

    match_ending_reason = _decrement_player_stamina(player, current_turn)
    if match_ending_reason:
        # Player has lost due to fatigue
        return match_ending_reason

    _increment_current_player_mp(player, match_context.current_turn)
    _process_cell_states(match_context)


def _decrement_player_stamina(player: Player, current_turn: int):
    if current_turn <= 2:
        return None

    player_resources = player.resources
    player_resources.current_stamina = max(0, player_resources.current_stamina - 1)

    if player_resources.current_stamina > 0:
        return None

    # Player has lost stamina, so we need to decrement their HP
    # and check if they have lost the game due to fatigue
    player.match_data.fatigue_damage += 1
    player_resources.current_hp -= player.match_data.fatigue_damage
    if player_resources.current_hp <= 0:
        return EndingReason.FATIGUE


def _increment_current_player_mp(player: Player, current_turn: int):
    """
    Increments the current player's available mana points for the turn by 1.
    """
    remainder = current_turn % 2
    quotient = current_turn // 2

    player_resources = player.resources
    player_resources.current_mp = min(quotient + remainder, player_resources.max_mp)


def _process_cell_states(match_context: MatchContext):
    """
    Cells cannot move nor attack on the turn they are spawned, so
    we "wake them up" during the next turn.
    """
    current_player_cells = match_context.game_board.get_cells_owned_by_player(
        player1=match_context.is_player1_turn,
    )
    other_player_cells = match_context.game_board.get_cells_owned_by_player(
        player1=not match_context.is_player1_turn,
    )
    for cell in current_player_cells:
        for state in STATES_TO_CLEAR_AT_TURN_BEGINNING:
            if cell.has_state(state):
                cell.remove_state(state)

    for cell in other_player_cells:
        for state in STATES_TO_CLEAR_AT_TURN_END:
            if cell.has_state(state):
                cell.remove_state(state)
