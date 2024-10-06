from venv import logger

from flask import session

from constants.session_variables import (
    PLAYER_INFO,
    ROOM_ID,
    SESSION_ID,
    SOCKET_CONNECTED,
)


def session_initialized():
    return SESSION_ID in session


def socket_connected():
    return session.get(SOCKET_CONNECTED) is True


def clear_match_info():
    """
    Removes all of the match information from the session, such as the room
    id or player info.
    """
    logger.debug("Clearing session match info")
    del session[ROOM_ID]
    del session[PLAYER_INFO]
