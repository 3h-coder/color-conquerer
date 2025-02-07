from flask import request, session
from flask_socketio import emit, join_room

from config.logging import get_configured_logger
from constants.session_variables import IN_MATCH, PLAYER_INFO, ROOM_ID, SESSION_ID
from dto.cell_dto import CellDto
from dto.message_dto import MessageDto
from dto.player_dto import PlayerDto
from events.events import Events
from exceptions.server_error import ServerError
from game_engine.models.player import Player
from server_gate import get_match_handler, get_session_cache_handler
from utils import session_utils

_logger = get_configured_logger(__name__)


def only_if_in_match(func):
    """
    Decorator that only allows the execution of the decorated function if the
    player is in a match, uing the session variable IN_MATCH.
    """

    def wrapper(*args, **kwargs):
        if not session_utils.is_in_match():
            _logger.error(
                f"({request.remote_addr}) | Tried to execute a match event outside of a match"
            )
            return
        return func(*args, **kwargs)

    return wrapper


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

    join_room(room_id)
    match = match_handler.get_unit(room_id)
    session[IN_MATCH] = True

    # Notify the client so it can render accordingly
    if match.is_ongoing():
        emit(
            Events.SERVER_MATCH_ONGOING,
            match.get_turn_context_dto().to_dict(),
        )
    elif match.is_waiting_to_start():
        match.mark_player_as_ready(player_info.player_id)
        # Start the match if everyone is ready
        if match.all_players_ready():
            _logger.info(f"All players ready in the room {room_id}")
            match.start()
        # Otherwise notify the user that we're still waiting for their opponent
        else:
            emit(
                Events.SERVER_SET_WAITING_TEXT,
                MessageDto("Waiting for your opponent...").to_dict(),
            )


@only_if_in_match
def handle_turn_end():
    """
    Sent by the client when a player choose's to end their turn by clicking
    the end turn button.
    """
    room_id = _get_session_variable(ROOM_ID)
    player_info: Player = _get_session_variable(PLAYER_INFO)
    _logger.info(f"({request.remote_addr}) | Turn swap requested")

    match_handler = get_match_handler()

    match = match_handler.get_unit(room_id)
    if not match.get_current_player().player_id == player_info.player_id:
        _logger.error(
            "The end of turn can only be requested by the player whose turn it is"
        )
        return
    match.force_turn_swap()


def handle_session_clearing():
    """
    Sent by the client when after acknowledging the end of a match.
    Clears all the match related session variables so they may queue for a new match.
    """
    session_utils.clear_match_info()


@only_if_in_match
def handle_cell_hover(data: dict):
    """
    Notifies the room (i.e. the opponent) that a certain cell is being hovered.
    """
    cell_info = CellDto.from_dict(data)
    room_id = _get_session_variable(ROOM_ID)
    emit(
        Events.SERVER_CELL_HOVER,
        cell_info.to_dict(),
        to=room_id,
        broadcast=True,
    )


@only_if_in_match
def handle_cell_hover_end(data: dict):
    """
    Notifies the room (i.e. the opponent) that a certain cell is no longer being hovered.
    """
    cell_info_dto = CellDto.from_dict(data)
    room_id = _get_session_variable(ROOM_ID)
    emit(
        Events.SERVER_CELL_HOVER_END,
        cell_info_dto.to_dict(),
        to=room_id,
        broadcast=True,
    )


@only_if_in_match
def handle_cell_click(data: dict):
    """
    Receives the client cell click, and notifies the client accordingly.
    """
    room_id = _get_session_variable(ROOM_ID)
    player_info: Player = _get_session_variable(PLAYER_INFO)
    match = get_match_handler().get_unit(room_id)

    player_id = player_info.player_id
    if not match.get_current_player().player_id == player_id:
        _logger.error(
            f"Cannot process the click of the player {player_id} as it is the turn of their opponent"
        )
        return

    cell_info = CellDto.from_dict(data)
    _logger.info(f"({request.remote_addr}) | Received cell click event -> {cell_info}")
    row, col = cell_info.rowIndex, cell_info.columnIndex
    match.handle_cell_selection(row, col)


@only_if_in_match
def handle_spawn_button():
    """
    Receives the client's request to spawn a unit.
    """
    _logger.info(f"({request.remote_addr}) | Received cell spawn button toggle event")
    room_id = _get_session_variable(ROOM_ID)
    player_info: Player = _get_session_variable(PLAYER_INFO)
    match = get_match_handler().get_unit(room_id)

    player_id = player_info.player_id
    if not match.get_current_player().player_id == player_id:
        _logger.error(
            f"Cannot process the spawn request of the player {player_id} as it is the turn of their opponent"
        )
        return

    match.handle_spawn_button()


@only_if_in_match
def handle_spell_button(spell_id: int):
    """
    Receives the client's request to use a spell.
    """
    _logger.info(f"({request.remote_addr}) | Received spell button toggle event")
    room_id = _get_session_variable(ROOM_ID)
    player_info: Player = _get_session_variable(PLAYER_INFO)
    match = get_match_handler().get_unit(room_id)

    player_id = player_info.player_id
    if not match.get_current_player().player_id == player_id:
        _logger.error(
            f"Cannot process the spell request of the player {player_id} as it is the turn of their opponent"
        )
        return

    match.handle_spell_button(spell_id)


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
