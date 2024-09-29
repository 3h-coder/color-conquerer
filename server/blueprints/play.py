from flask import Blueprint, jsonify, session, request
from flask_socketio import join_room

from config.logger import logger
from constants.session_variables import PLAYER_INFO, ROOM_ID
from dto.game_context_dto import GameContextDto
from dto.player_info_dto import PlayerInfoDto
from exceptions.unauthorized import UnauthorizedError
from exceptions.wrong_data_error import WrongDataError
from handlers import match_handler
from middlewares.error_handler import handle_error

play_bp = Blueprint("play", __name__)
play_bp.register_error_handler(Exception, handle_error)


@play_bp.route("/play/match-info", methods=["GET"])
def get_match_info():
    raise UnauthorizedError("Lalala")
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

@play_bp.route("/play/game-context", methods=["POST"])
def confirm_ids():
    """
    This route is called when the client failed to retrieve the room id
    and player id from the routes above
    """
    logger.info("Resorting to saved data context retrieval")

    errorMessage = "An error occured while trying to connect to your match"
    player_id = request.form.get("playerId")
    if player_id is None:
        logger.error("No player id provided")
        raise WrongDataError(errorMessage, socket_connection_killer=True)
    
    room_id = request.form.get("roomId")
    if room_id is None:
        logger.error("No room id provided")
        raise WrongDataError(errorMessage, socket_connection_killer=True)
    
    mhu = match_handler.get_unit(room_id)
    if mhu is None:
        raise WrongDataError(errorMessage, socket_connection_killer=True, code=404)
    
    player_ids = [mhu.match_info.player1.playerId, mhu.match_info.player2.playerId]
    if player_id not in player_ids:
        logger.error(f"The player id {player_id} does not exist in the room {room_id}")
        raise WrongDataError(errorMessage, socket_connection_killer=True, code=404)
    
    player_info = mhu.get_player(player_id)

    return jsonify(GameContextDto(mhu.match_info, player_info).to_dict()), 200
