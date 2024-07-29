from flask import session
from handlers import match_handler

from config.config import logger
from session_variables import SOCKET_CONNECTED, PLAYER_INFO, ROOM_ID, IN_MATCH


def handle_connection():
    session[SOCKET_CONNECTED] = True
    logger.debug("----- Socket connection -----")

    room_id = session.get(ROOM_ID)
    if not room_id:
        return

    logger.debug(f"what is session.get(IN_MATCH) ? : {session.get(IN_MATCH)}")
    if session.get(IN_MATCH) is True:
        match_handler.get_unit(room_id).stop_exit_watch(session.get(PLAYER_INFO))

