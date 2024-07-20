from flask import Blueprint, jsonify, session

from config.config import logger
from dto.player_info_dto import PlayerInfoDto
from exceptions.unauthorized import UnauthorizedError
from handlers import match_handler
from middlewares.error_handler import handle_error

play_bp = Blueprint("play", __name__)
play_bp.register_error_handler(Exception, handle_error)


@play_bp.route("/play/match-info", methods=["GET"])
def get_match_info():
    room_id = session.get("room_id")
    logger.info(f"session is {session}")
    logger.info(f"room_id is {room_id}")

    if not room_id:
        raise UnauthorizedError("Could not resolve the room")

    match_info = match_handler.get_match_info(room_id)
    return jsonify(match_info.to_dict()), 200


@play_bp.route("/play/player-info", methods=["GET"])
def get_player_info():
    player_info: PlayerInfoDto = session.get("player_info")

    if not player_info:
        raise UnauthorizedError("Could not resolve player information")

    return jsonify(player_info.to_dict()), 200
