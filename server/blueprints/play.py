from flask import Blueprint, jsonify, session

from config.config import logger
from dto.player_info_dto import PlayerInfoDto
from exceptions.unauthorized import UnauthorizedError
from handlers import match_handler
from middlewares.error_handler import handle_error
from session_variables import IN_MATCH, PLAYER_INFO, ROOM_ID

play_bp = Blueprint("play", __name__)
play_bp.register_error_handler(Exception, handle_error)


@play_bp.route("/play/match-info", methods=["GET"])
def get_match_info():
    room_id = session.get(ROOM_ID)

    if not room_id:
        raise UnauthorizedError("Could not resolve the room")

    match_info = match_handler.get_match_info(room_id)
    return jsonify(match_info.to_dict()), 200


@play_bp.route("/play/player-info", methods=["GET"])
def get_player_info():
    player_info: PlayerInfoDto | None = session.get(PLAYER_INFO)

    if not player_info:
        raise UnauthorizedError("Could not resolve player information")

    session[IN_MATCH] = True
    logger.debug(f"what is session.get(IN_MATCH) ? : {session.get(IN_MATCH)}")
    return jsonify(player_info.to_dict()), 200
