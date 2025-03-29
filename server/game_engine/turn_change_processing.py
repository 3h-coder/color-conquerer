from constants.game_constants import (
    STATES_TO_CLEAR_AT_TURN_BEGINNING,
    STATES_TO_CLEAR_AT_TURN_END,
)
from game_engine.models.match_context import MatchContext


def process_turn_change(match_context: MatchContext):
    match_context.current_turn += 1
    match_context.is_player1_turn = not match_context.is_player1_turn

    _increment_current_player_mp(match_context)
    _process_cell_states(match_context)


def _increment_current_player_mp(match_context: MatchContext):
    """
    Increments the current player's available mana points for the turn by 1.
    """
    current_turn = match_context.current_turn
    current_player = match_context.get_current_player()

    player_game_info = current_player.resources

    remainder = current_turn % 2
    quotient = current_turn // 2

    player_game_info.current_mp = min(quotient + remainder, player_game_info.max_mp)


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
