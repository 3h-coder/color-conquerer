from flask import request, session
from flask_socketio import emit

from config.logging import get_configured_logger
from constants.session_variables import PLAYER_INFO, ROOM_ID, SOCKET_CONNECTED
from dto.misc.message_dto import MessageDto
from events.events import Events
from game_engine.models.dtos.player import Player
from server_gate import get_connection_handler, get_match_handler

_logger = get_configured_logger(__name__)


def handle_connection(_):
    """
    Handles all of the possible action when a socket (re)connection occurs.

    Does nothing if the socket connection is multiple.
    """
    connection_handler = get_connection_handler()

    connection_handler.register_connection(request.remote_addr)
    session[SOCKET_CONNECTED] = True

    if not connection_handler.single_connection():
        return

    room_id = session.get(ROOM_ID)
    if not room_id:
        return

    match_handler = get_match_handler()

    match = match_handler.get_unit(room_id)
    if match is None:
        return

    if match.is_ongoing():
        _logger.debug("Player rejoinded the match, stopping exit watcher")
        player_info: Player = session.get(PLAYER_INFO)
        player_id = player_info.player_id
        match.stop_watching_player_exit(player_id)
    elif match.is_ended():
        _logger.debug(
            "Player rejoined, but the match already ended. Redirecting them to the home page"
        )
        emit(Events.SERVER_REDIRECT, MessageDto("/").to_dict())
