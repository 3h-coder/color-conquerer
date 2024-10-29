from flask import Blueprint, current_app, jsonify, request, session

from constants.session_variables import PLAYER_INFO, ROOM_ID, SESSION_ID
from dto.partial_player_info_dto import PartialPlayerInfoDto
from exceptions.unauthorized_error import UnauthorizedError
from handlers import match_handler, session_cache_handler
from middlewares.error_handler import handle_error
from utils import session_utils

play_bp = Blueprint("play", __name__)
play_bp.register_error_handler(Exception, handle_error)


@play_bp.route("/play/match-info", methods=["GET"])
def get_match_info():
    room_id = session.get(ROOM_ID)
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

    match_info = match_handler.get_match_info(room_id, partial=True)
    return jsonify(match_info.to_dict()), 200


@play_bp.route("/play/player-info", methods=["GET"])
def get_player_info():
    player_info = session.get(PLAYER_INFO)
    if player_info is None:
        current_app.logger.warning(
            f"({request.remote_addr}) | The player info was not defined, resorting to session cache"
        )
        session_cache = session_cache_handler.get_cache_for_session(session[SESSION_ID])
        player_info = session_cache.get(PLAYER_INFO)
        if not player_info:
            raise UnauthorizedError("Could not resolve player information")
        session_utils.save_into_session(PLAYER_INFO, player_info)

    partial_player_info = PartialPlayerInfoDto.from_player_info_dto(player_info)
    return jsonify(partial_player_info.to_dict()), 200
