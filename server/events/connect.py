from flask import session

from config.config import logger
from handlers import match_handler
from handlers.match_handler_unit import MatchStatus
from session_variables import PLAYER_INFO, ROOM_ID, SOCKET_CONNECTED


def handle_connection():
    session[SOCKET_CONNECTED] = True
    logger.debug("----- Socket connection -----")

    room_id = session.get(ROOM_ID)
    if not room_id:
        return

    mhu = match_handler.get_unit(room_id)

    if mhu.is_ongoing():
        mhu.stop_exit_watch(session.get(PLAYER_INFO))
