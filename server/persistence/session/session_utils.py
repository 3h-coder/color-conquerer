import logging

import redis
from flask import current_app, make_response, session

from config.app_config import AppConfigKeys, AppSessionType
from persistence.session.models.session_player import SessionPlayer
from persistence.session.session_variables import (
    IN_MATCH,
    PLAYER_INFO,
    ROOM_ID,
    SESSION_ID,
    SOCKET_CONNECTED,
)
from server_gate import get_session_cache_handler


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


def forcefully_save_session():
    """
    To be use when you need to have certain session values saved before the end of a request.
    """
    session.modified = True
    current_app.session_interface.save_session(current_app, session, make_response())


def get_session_player():
    raw_session_player = session.get(PLAYER_INFO)
    return (
        raw_session_player
        if isinstance(raw_session_player, SessionPlayer)
        else SessionPlayer.from_dict(raw_session_player)
    )


def refresh_session_lifetime(logger: logging.Logger = None):
    """
    Extends/resets the session's lifetime in Redis by updating its TTL.
    Call this function whenever you want to prevent the session from expiring.
    """
    session.modified = True

    if not current_app.config.get(AppConfigKeys.SESSION_TYPE) == AppSessionType.REDIS:
        return

    redis_connection: redis.Redis = current_app.config.get(AppConfigKeys.SESSION_REDIS)
    session_key = current_app.config.get(AppConfigKeys.SESSION_KEY_PREFIX)
    session_id = session.sid if hasattr(session, "sid") else None
    if session_id:
        redis_key = f"{session_key}{session_id}"
        redis_connection.expire(
            redis_key,
            int(current_app.config.get(AppConfigKeys.PERMANENT_SESSION_LIFETIME)),
        )
    elif logger:
        logger.warning(
            "Unable to extend the session's lifetime duration as the session_id is not defined"
        )


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
