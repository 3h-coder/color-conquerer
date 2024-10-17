from flask import request, session

from config.logging import get_configured_logger
from constants.session_variables import PLAYER_INFO, ROOM_ID, SOCKET_CONNECTED
from handlers import connection_handler, match_handler

_logger = get_configured_logger(__name__)


def handle_connection(_):
    """
    Handles all of the possible action when a socket (re)connection occurs.

    Does nothing if the socket connection is multiple.
    """
    connection_handler.register_connection(request.remote_addr)
    session[SOCKET_CONNECTED] = True

    if not connection_handler.single_connection():
        return

    room_id = session.get(ROOM_ID)
    if not room_id:
        return

    mhu = match_handler.get_unit(room_id)
    if mhu is None:
        return

    if mhu.is_ongoing():
        _logger.debug("Player rejoinded the match, stopping exit watcher")
        player_id = session.get(PLAYER_INFO).playerId
        mhu.stop_watching_player_exit(player_id)
    elif mhu.is_ended():
        _logger.debug("Player rejoined, but the match already ended")
