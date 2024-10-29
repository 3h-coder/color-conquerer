from venv import logger

from flask import session

from constants.session_variables import (
    PLAYER_INFO,
    ROOM_ID,
    SESSION_ID,
    SOCKET_CONNECTED,
)


def get_session_data():
    return dict(session)


def session_initialized():
    return SESSION_ID in session


def socket_connected():
    return session.get(SOCKET_CONNECTED) is True


def save_into_session(key: str, value):
    session[key] = value
    session.modified = True


def clear_match_info():
    """
    Removes all of the match information from the session, such as the room
    id or player info.
    """
    logger.debug("Clearing session match info")
    safe_delete(ROOM_ID)
    safe_delete(PLAYER_INFO)


def safe_delete(session_variable: str):
    """
    Deletes a variable from the session safely.
    """
    try:
        del session[session_variable]
    except KeyError:
        pass
