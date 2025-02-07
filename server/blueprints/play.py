from flask import Blueprint, current_app, jsonify, request, session

from constants.session_variables import PLAYER_INFO, ROOM_ID, SESSION_ID
from dto.player_dto import PlayerDto
from exceptions.unauthorized_error import UnauthorizedError
from game_engine.models.match_context import MatchContext
from game_engine.models.player import Player
from handlers.session_cache_handler import SessionCacheHandler
from middlewares.error_handler import handle_error
from server_gate import get_match_handler, get_session_cache_handler
from utils import session_utils

play_bp = Blueprint("play", __name__)
play_bp.register_error_handler(Exception, handle_error)


@play_bp.route("/play/match-info", methods=["GET"])
def get_match_info():
    session_cache_handler = get_session_cache_handler()
    room_id = _get_room_id_or_raise_error(session_cache_handler)

    match_handler = get_match_handler()

    match_context: MatchContext = match_handler.get_match_context(room_id)
    return jsonify(match_context.to_dto().to_dict()), 200


@play_bp.route("/play/player-info", methods=["GET"])
def get_player_info():
    session_cache_handler = get_session_cache_handler()
    player_info: Player = _get_player_info_or_raise_error(session_cache_handler)

    player_info_dto = player_info.to_dto()
    return jsonify(player_info_dto.to_dict()), 200


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
            f"({request.remote_addr}) | The room id was not defined, resorting to session cache"
        )
        session_cache = session_cache_handler.get_cache_for_session(session[SESSION_ID])
        room_id = session_cache.get(ROOM_ID)
        if not room_id:
            raise UnauthorizedError("Could not resolve the room")
        session_utils.save_into_session(ROOM_ID, room_id)

    return room_id


def _get_player_info_or_raise_error(session_cache_handler: SessionCacheHandler):
    """
    Tries to get the player info from the session or session cache.
    If it fails to get it, throws an unauthorized error.
    """
    player_info: PlayerDto = session.get(PLAYER_INFO)
    if player_info is None:
        current_app.logger.warning(
            f"({request.remote_addr}) | The player info was not defined, resorting to session cache"
        )
        session_cache = session_cache_handler.get_cache_for_session(session[SESSION_ID])
        player_info = session_cache.get(PLAYER_INFO)
        if not player_info:
            raise UnauthorizedError("Could not resolve player information")
        session_utils.save_into_session(PLAYER_INFO, player_info)

    return player_info
