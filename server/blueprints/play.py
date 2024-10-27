from flask import Blueprint, jsonify, session, current_app

from constants.session_variables import PLAYER_INFO, ROOM_ID
from dto.partial_player_info_dto import PartialPlayerInfoDto
from exceptions.unauthorized_error import UnauthorizedError
from handlers import match_handler
from middlewares.error_handler import handle_error
from utils import session_utils

play_bp = Blueprint("play", __name__)
play_bp.register_error_handler(Exception, handle_error)


@play_bp.route("/play/match-info", methods=["GET"])
def get_match_info():
    current_app.logger.debug(f"Session data is : {session_utils.get_session_data()}")
    room_id = session.get(ROOM_ID)
    if not room_id:
        raise UnauthorizedError("Could not resolve the room")

    match_info = match_handler.get_match_info(room_id, partial=True)
    return jsonify(match_info.to_dict()), 200


@play_bp.route("/play/player-info", methods=["GET"])
def get_player_info():
    player_info = session.get(PLAYER_INFO)
    if player_info is None:
        raise UnauthorizedError("Could not resolve player information")

    partial_player_info = PartialPlayerInfoDto.from_player_info_dto(player_info)
    return jsonify(partial_player_info.to_dict()), 200
