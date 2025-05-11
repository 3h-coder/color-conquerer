from flask import request, session
from flask_socketio import emit

from config.logging import get_configured_logger
from dto.misc.message_dto import MessageDto
from events.events import Events
from server_gate import get_connection_handler, get_match_handler
from session_management.models.session_player import SessionPlayer
from session_management.session_variables import PLAYER_INFO, ROOM_ID, SOCKET_CONNECTED
from utils import logging_utils

_logger = get_configured_logger(
    __name__, prefix_getter=lambda: logging_utils.flask_request_remote_addr_prefix()
)


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
        # Room id but no match
        # Session clearing will be handled by the home blueprint
        return

    if match.is_ongoing():
        _logger.debug("Player rejoinded the match, stopping exit watcher")

        player_info: SessionPlayer = session.get(PLAYER_INFO)
        match.stop_watching_player_exit(player_info.player_id)

    elif match.is_ended():
        _logger.debug(
            "Player rejoined, but the match already ended. Redirecting them to the home page"
        )
        # The home blueprint will help display a message at the top saying that
        # the player lost their match as they left it
        emit(Events.SERVER_HOME_ERROR_REDIRECT, MessageDto("").to_dict())
