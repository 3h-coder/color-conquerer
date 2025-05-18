from functools import wraps

from flask import request, session
from flask_socketio import emit, join_room

from config.logging import get_configured_logger
from dto.cell.cell_dto import CellDto
from events.events import Events
from events.shared_notifications import match_launch_error_redirect
from exceptions.server_error import ServerError
from game_engine.models.match.match_closure_info import EndingReason
from handlers.match_handler_unit import MatchHandlerUnit
from server_gate import get_match_handler, get_server, get_session_cache_handler
from session_management import session_utils
from session_management.models.session_player import SessionPlayer
from session_management.session_variables import (
    IN_MATCH,
    PLAYER_INFO,
    ROOM_ID,
    SESSION_ID,
)
from utils import logging_utils

SERVER_ERROR_MSG = "A server error occured, unable to connect you to your match"
_logger = get_configured_logger(
    __name__, prefix_getter=lambda: logging_utils.flask_request_remote_addr_prefix()
)

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
            room_id = _get_room_id_or_raise_error()
            player_info: SessionPlayer = _get_player_info_or_raise_error()
            match = get_match_handler().get_unit(room_id)

            if match is None:
                _logger.critical("Could not process the action as there is no match")
                return

            if not match.is_ongoing():
                _logger.error(
                    f"Could not process the action as the match is not ongoing (the match status is {match.status.name})"
                )
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

    # NOTE : the play blueprint should already redirect the player if the following
    # session variables cannot be resolved, but this is an additional safety measure.
    # The match entry watcher should cancel the match if an exception is raised here as the
    # player will not be able to join it.
    player_info: SessionPlayer = _get_player_info_or_raise_error()
    room_id = _get_room_id_or_raise_error()

    match_handler = get_match_handler()
    match = match_handler.get_unit(room_id)

    if match.is_cancelled():
        _logger.info(
            f"({request.remote_addr}) | The player was ready but the match got cancelled"
        )
        match_launch_error_redirect()

    _join_socket_rooms(room_id, player_info.individual_room_id)
    session[IN_MATCH] = True

    # Notify the client so it can render accordingly
    if match.is_ongoing():
        emit(
            Events.SERVER_MATCH_ONGOING,
            match.get_turn_context_dto(for_player1=player_info.is_player1).to_dict(),
        )

    elif match.is_waiting_to_start():
        match.mark_player_as_ready(player_info.player_id)
        # Start the match if everyone is ready
        if match.all_players_ready():
            _logger.info(f"All players ready in the room {room_id}")
            match.start(with_countdown=not get_server().testing)
        # Otherwise notify the user that we're still waiting for their opponent
        else:
            emit(Events.SERVER_WAITING_FOR_OPPONENT)


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
    player_info: SessionPlayer = session_utils.get_session_player()
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
    Sent by the client after acknowledging the end of a match.
    Clears all the match related session variables so they may queue for a new match.
    """
    session_utils.clear_match_info()


def _join_socket_rooms(room_id: str, individual_room_id: str):
    join_room(room_id)
    join_room(individual_room_id)


def _get_player_info_or_raise_error():
    player_info = _get_session_variable(PLAYER_INFO)
    return (
        player_info
        if isinstance(player_info, SessionPlayer)
        else SessionPlayer.from_dict(player_info)
    )


def _get_room_id_or_raise_error():
    return _get_session_variable(ROOM_ID)


def _get_session_variable(variable_name: str):
    if SESSION_ID not in session:
        _logger.error(
            f"({request.remote_addr}) | The session id is not defined, therefore the player cannot be in a match"
        )
        raise ServerError(SERVER_ERROR_MSG, socket_connection_killer=True)

    value = session.get(variable_name)
    if value is None:
        _logger.error(
            f"({request.remote_addr}) | {variable_name} was None, resorting to session cache."
        )
        session_cache = get_session_cache_handler().get_cache_for_session(
            session[SESSION_ID]
        )
        value = session_cache.get(variable_name)

    if value is None:
        _logger.error(
            f"({request.remote_addr}) | {variable_name} was still None, raising a server error."
        )
        raise ServerError(SERVER_ERROR_MSG, socket_connection_killer=True)

    return value
