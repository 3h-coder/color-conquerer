from flask import request, session
from flask_socketio import emit, join_room

from config.logging import get_configured_logger
from constants.session_variables import IN_MATCH, PLAYER_INFO, ROOM_ID, SESSION_ID
from dto.cell_info_dto import CellInfoDto
from dto.message_dto import MessageDto
from dto.server_only.player_info_dto import PlayerInfoDto
from dto.turn_info_dto import TurnInfoDto
from events.events import Events
from exceptions.server_error import ServerError
from handlers import match_handler, session_cache_handler
from utils import session_utils

_logger = get_configured_logger(__name__)


def handle_client_ready():
    """
    Receives the signal of the given player's client and marks the player ready
    server side, possibly starting the match if everyone is.
    """
    server_error_msg = "A server error occured, unable to connect you to your match"

    player_info: PlayerInfoDto = _get_session_variable(PLAYER_INFO)
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

    join_room(room_id)
    match = match_handler.get_unit(room_id)
    match.players_ready[player_info.playerId] = True
    session[IN_MATCH] = True

    # Notify the client so it can render accordingly
    if match.is_ongoing():
        emit(
            Events.SERVER_MATCH_ONGOING.value,
            TurnInfoDto(
                match.get_current_player_id(),
                match.match_info.isPlayer1Turn,
                match.get_remaining_turn_time(),
                notifyTurnChange=False,
            ).to_dict(),
        )
    elif match.is_waiting_to_start():
        # Start the match if everyone is ready
        if all(value is True for value in match.players_ready.values()):
            _logger.info(f"All players ready in the room {room_id}")
            match.start()
        # Otherwise notify the user that we're still waiting for their opponent
        else:
            emit(
                Events.SERVER_SET_WAITING_TEXT.value,
                MessageDto.from_string("Waiting for your opponent...").to_dict(),
            )


def handle_session_clearing():
    """
    Sent by the client when after acknowledging the end of a match.
    Clears all the match related session variables so they may queue for a new match.
    """
    session_utils.clear_match_info()


def handler_cell_hover(data: dict):
    """
    Notifies the room (i.e. the opponent) that a certain cell is being hovered.
    """
    cell_info_dto = CellInfoDto.from_dict(data)
    room_id = _get_session_variable(ROOM_ID)
    emit(
        Events.SERVER_CELL_HOVER.value,
        cell_info_dto.to_dict(),
        to=room_id,
        broadcast=True,
    )


def handler_cell_hover_end(data: dict):
    """
    Notifies the room (i.e. the opponent) that a certain cell is no longer being hovered.
    """
    cell_info_dto = CellInfoDto.from_dict(data)
    room_id = _get_session_variable(ROOM_ID)
    emit(
        Events.SERVER_CELL_HOVER_END.value,
        cell_info_dto.to_dict(),
        to=room_id,
        broadcast=True,
    )


def _get_session_variable(variable_name: str):
    value = session.get(variable_name)
    if value is None:
        _logger.error(
            f"({request.remote_addr}) | {variable_name} was None, resorting to session cache"
        )
        session_cache = session_cache_handler.get_cache_for_session(session[SESSION_ID])
        value = session_cache.get(variable_name)

    return value
