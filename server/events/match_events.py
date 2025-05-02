from functools import wraps

from flask import request, session
from flask_socketio import emit, join_room

from config.logging import get_configured_logger
from constants.session_variables import IN_MATCH, PLAYER_INFO, ROOM_ID, SESSION_ID
from dto.cell.cell_dto import CellDto
from events.events import Events
from exceptions.server_error import ServerError
from game_engine.models.dtos.match_closure import EndingReason
from game_engine.models.player.player import Player
from handlers.match_handler_unit import MatchHandlerUnit
from server_gate import get_match_handler, get_session_cache_handler
from utils import session_utils

_logger = get_configured_logger(__name__)

# Used in tests as well
OUT_OF_MATCH_LOG_ERROR_MSG = "Tried to execute a match event outside of a match"


def only_if_in_match(func):
    """
    Decorator that only allows the execution of the decorated function if the
    player is in a match, uing the session variable IN_MATCH.
    """

    def wrapper(*args, **kwargs):
        if not session_utils.is_in_match():
            _logger.error(f"({request.remote_addr}) | {OUT_OF_MATCH_LOG_ERROR_MSG}")
            return
        return func(*args, **kwargs)

    return wrapper


def only_if_current_turn(error_log_msg: str):
    """
    Decorator that only allows the execution of an action if the
    player requesting it is the current player (i.e. the player whose turn it is)
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            room_id = _get_session_variable(ROOM_ID)
            player_info: Player = _get_session_variable(PLAYER_INFO)
            match = get_match_handler().get_unit(room_id)

            if match is None:
                _logger.critical("Could not process the action as there is no match")
                return

            player_id = player_info.player_id
            if not match.get_current_player().player_id == player_id:
                default_msg = "Cannot process the action as it is not the player's turn"
                log_message = (
                    error_log_msg if error_log_msg is not None else default_msg
                )
                _logger.error(log_message)
                return

            func(match, *args, **kwargs)

        return wrapper

    # If "func" is passed directly (without parentheses), return the decorator applied to func
    if callable(error_log_msg):
        # Treat "error_log_msg" as the function
        return decorator(error_log_msg)
    # Otherwise, return the decorator normally
    return decorator


def handle_client_ready():
    """
    Receives the signal of the given player's client and marks the player ready
    server side, possibly starting the match if everyone is.
    """
    server_error_msg = "A server error occured, unable to connect you to your match"

    player_info: Player = _get_session_variable(PLAYER_INFO)
    if player_info is None:
        raise ServerError(
            server_error_msg,
            socket_connection_killer=True,
        )

    room_id = _get_session_variable(ROOM_ID)
    if room_id is None:
        raise ServerError(
            server_error_msg,
            socket_connection_killer=True,
        )

    match_handler = get_match_handler()
    match = match_handler.get_unit(room_id)

    _join_socket_rooms(room_id, player_info)
    session[IN_MATCH] = True

    # Notify the client so it can render accordingly
    if match.is_ongoing():
        emit(
            Events.SERVER_MATCH_ONGOING,
            match.get_turn_context_dto(for_player1=player_info.is_player_1).to_dict(),
        )

    elif match.is_waiting_to_start():
        match.mark_player_as_ready(player_info.player_id)
        # Start the match if everyone is ready
        if match.all_players_ready():
            _logger.info(f"All players ready in the room {room_id}")
            match.start()
        # Otherwise notify the user that we're still waiting for their opponent
        else:
            emit(Events.SERVER_WAITING_FOR_OPPONENT)


@only_if_in_match
def handle_client_spells_request():
    """
    Sent by the client when the player expands their spell board or
    after the player casts a spell.

    This is to display the updated spell deck.
    """
    player_info: Player = _get_session_variable(PLAYER_INFO)
    room_id = _get_session_variable(ROOM_ID)

    match_handler = get_match_handler()
    match = match_handler.get_unit(room_id)

    player_resources = match.get_players_resources()
    spells_dto = (
        player_resources[0].get_spells_dto()
        if player_info.is_player_1
        else player_resources[1].get_spells_dto()
    )

    emit(Events.SERVER_SEND_SPELLS, spells_dto.to_dict())


@only_if_in_match
@only_if_current_turn(
    "The end of turn can only be requested by the player whose turn it is"
)
def handle_turn_end(match: MatchHandlerUnit):
    """
    Sent by the client when a player choose's to end their turn by clicking
    the end turn button.
    """
    match.force_turn_swap()


@only_if_in_match
def handle_match_concede():
    """
    Receives the client match concession request, and ends the match.
    """
    player_info: Player = _get_session_variable(PLAYER_INFO)
    player_id = player_info.player_id
    room_id = _get_session_variable(ROOM_ID)

    match_handler = get_match_handler()
    match = match_handler.get_unit(room_id)

    match.end(EndingReason.PLAYER_CONCEDED, loser_id=player_id)


@only_if_in_match
@only_if_current_turn(
    "Cannot process the click of the player as it is the turn of their opponent"
)
def handle_cell_click(match: MatchHandlerUnit, data: dict):
    """
    Receives the client cell click, and notifies the client accordingly.
    """
    cell_info = CellDto.from_dict(data)
    row, col = cell_info.rowIndex, cell_info.columnIndex
    match.handle_cell_selection(row, col)


@only_if_in_match
@only_if_current_turn(
    "Cannot process the spawn request as it is the turn of their opponent"
)
def handle_spawn_button(match: MatchHandlerUnit):
    """
    Receives the client's request to spawn a unit.
    """
    match.handle_spawn_button()


@only_if_in_match
@only_if_current_turn(
    "Cannot process the spell request of the player as it is the turn of their opponent"
)
def handle_spell_button(match: MatchHandlerUnit, spell_id: int):
    """
    Receives the client's request to use a spell.
    """
    _logger.info(
        f"({request.remote_addr}) | Received the spell request -> spell id : {spell_id}"
    )
    match.handle_spell_button(spell_id)


def handle_session_clearing():
    """
    Sent by the client when after acknowledging the end of a match.
    Clears all the match related session variables so they may queue for a new match.
    """
    session_utils.clear_match_info()


def _join_socket_rooms(room_id: str, player_info: Player):
    # Join the common room
    join_room(room_id)
    join_room(player_info.individual_room_id)


def _get_session_variable(variable_name: str):
    value = session.get(variable_name)
    if value is None:
        _logger.error(
            f"({request.remote_addr}) | {variable_name} was None, resorting to session cache"
        )
        session_cache = get_session_cache_handler().get_cache_for_session(
            session[SESSION_ID]
        )
        value = session_cache.get(variable_name)

    return value
