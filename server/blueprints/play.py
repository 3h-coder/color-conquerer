from functools import wraps

from flask import Blueprint, current_app, jsonify, request, session

from exceptions.unauthorized_error import UnauthorizedError
from game_engine.models.match.match_context import MatchContext
from handlers.session_cache_handler import SessionCacheHandler
from middlewares.error_handler import handle_error
from server_gate import get_match_handler, get_session_cache_handler
from session_management import session_utils
from session_management.models.session_player import SessionPlayer
from session_management.session_variables import PLAYER_INFO, ROOM_ID, SESSION_ID

play_bp = Blueprint("play", __name__)
play_bp.register_error_handler(Exception, handle_error)


@play_bp.route("/play/match-info", methods=["GET"])
def get_match_info():
    session_cache_handler = get_session_cache_handler()
    room_id = _get_room_id_or_raise_error(session_cache_handler)
    match_context = _get_match_context_or_raise_error(room_id)

    return jsonify(match_context.to_dto(None).to_dict()), 200


@play_bp.route("/play/player-info", methods=["GET"])
def get_player_info():
    session_cache_handler = get_session_cache_handler()
    player_info: SessionPlayer = _get_player_info_or_raise_error(session_cache_handler)

    player_info_dto = player_info.to_dto()
    return jsonify(player_info_dto.to_dict()), 200


def _only_if_session_initialized(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if SESSION_ID not in session:
            raise UnauthorizedError(
                f"({request.remote_addr}) | The user has no defined session id, and therefore cannot be in a match. Redirecting them to the home page."
            )
        return func(*args, **kwargs)

    return wrapper


@_only_if_session_initialized
def _get_room_id_or_raise_error(session_cache_handler: SessionCacheHandler):
    """
    Tries to get the room id from the session or session cache.
    If it fails to get it, throws an unauthorized error.
    """
    room_id: str = session.get(ROOM_ID)
    # Sometimes the session does not have the time to persist the changes
    # when the client navigation causes immediate requests
    if not room_id:
        current_app.logger.warning(
            f"({request.remote_addr}) | The room id was not defined, resorting to session cache."
        )
        session_cache = session_cache_handler.get_cache_for_session(session[SESSION_ID])
        room_id = session_cache.get(ROOM_ID)
        if not room_id:
            current_app.logger.error(
                f"({request.remote_addr}) | Could not resolve the room, and therefore they are not in a match. Redirecting them to the home page."
            )
            raise UnauthorizedError("Could not resolve the room")
        session_utils.save_into_session(ROOM_ID, room_id)

    return room_id


@_only_if_session_initialized
def _get_match_context_or_raise_error(room_id: str):
    """
    Tries to get the match context from the given room id.

    Sometimes the player has a room_id saved into the session but there is no match linked to it,
    in which case we force a session clearing and throw an unauthorized error.
    """
    match_handler = get_match_handler()
    match_context: MatchContext = match_handler.get_match_context(room_id)
    if match_context is None:
        current_app.logger.error(
            f"({request.remote_addr}) | The player had a room id set but no associated match exists, resetting their session and redirecting them to the home page."
        )
        session_utils.clear_match_info()
        raise UnauthorizedError("Could not resolve the match")
    return match_context


@_only_if_session_initialized
def _get_player_info_or_raise_error(session_cache_handler: SessionCacheHandler):
    """
    Tries to get the player info from the session or session cache.
    If it fails to get it, throws an unauthorized error.
    """
    player_info: SessionPlayer = session.get(PLAYER_INFO)
    if player_info is None:
        current_app.logger.warning(
            f"({request.remote_addr}) | The player info was not defined, resorting to session cache"
        )
        session_cache = session_cache_handler.get_cache_for_session(session[SESSION_ID])
        player_info = session_cache.get(PLAYER_INFO)
        if not player_info:
            current_app.logger.error(
                f"({request.remote_addr}) | Could not resolve the player information, and therefore they are not in a match. Redirecting them to the home page."
            )
            raise UnauthorizedError("Could not resolve player information")
        session_utils.save_into_session(PLAYER_INFO, player_info)

    return player_info
