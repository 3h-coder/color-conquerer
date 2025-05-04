from flask import session

from server_gate import get_session_cache_handler
from session_management.session_variables import (
    IN_MATCH,
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


def is_in_match():
    return session.get(IN_MATCH) is True


def save_into_session(key: str, value):
    session[key] = value
    session.modified = True


def clear_match_info():
    """
    Removes all of the match information from the session, such as the room
    id or player info.
    This also clears the corresponding values in the session cache.
    """
    safe_delete(ROOM_ID)
    safe_delete(PLAYER_INFO)
    session[IN_MATCH] = False

    session_cache = get_session_cache_handler().get_cache_for_session(
        session[SESSION_ID]
    )
    if session_cache:
        _safe_delete_from_dict(session_cache, ROOM_ID)
        _safe_delete_from_dict(session_cache, PLAYER_INFO)


def safe_delete(session_variable: str):
    """
    Deletes a variable from the session safely.
    """
    _safe_delete_from_dict(session, session_variable)


def _safe_delete_from_dict(dict: dict, key):
    try:
        del dict[key]
    except KeyError:
        pass
