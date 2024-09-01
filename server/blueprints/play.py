from flask import Blueprint, jsonify, session
from flask_socketio import join_room

from constants.session_variables import PLAYER_INFO, ROOM_ID
from dto.player_info_dto import PlayerInfoDto
from exceptions.unauthorized import UnauthorizedError
from handlers import match_handler
from middlewares.error_handler import handle_error

play_bp = Blueprint("play", __name__)
play_bp.register_error_handler(Exception, handle_error)


@play_bp.route("/play/match-info", methods=["GET"])
def get_match_info():
    room_id = session.get(ROOM_ID)

    if not room_id:
        raise UnauthorizedError("Could not resolve the room")

    # TODO: send a partial DTO instead
    match_info = match_handler.get_match_info(room_id)
    return jsonify(match_info.to_dict()), 200


@play_bp.route("/play/player-info", methods=["GET"])
def get_player_info():
    player_info = session.get(PLAYER_INFO)

    if player_info is None:
        raise UnauthorizedError("Could not resolve player information")

    return jsonify(player_info.to_dict()), 200
