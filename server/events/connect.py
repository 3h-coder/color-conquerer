from flask import request, session
from flask_socketio import emit

from config.logging import get_configured_logger
from dto.misc.message_dto import MessageDto
from events.events import Events
from server_gate import get_connection_handler, get_match_handler
from session_management.models.session_player import SessionPlayer
from session_management.session_variables import PLAYER_INFO, ROOM_ID, SOCKET_CONNECTED

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
        # Session clearing will be handled by the home blueprint
        return

    if match.is_ongoing():
        _logger.debug("Player rejoinded the match, stopping exit watcher")
        player_info: SessionPlayer = session.get(PLAYER_INFO)
        player_id = player_info.player_id
        match.stop_watching_player_exit(player_id)
    elif match.is_ended():
        _logger.debug(
            "Player rejoined, but the match already ended. Redirecting them to the home page"
        )
        emit(Events.SERVER_HOME_ERROR_REDIRECT, MessageDto("/").to_dict())
