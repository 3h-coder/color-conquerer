from flask import Blueprint, jsonify, request, session
from flask_socketio import join_room

from config.logger import logger
from constants.session_variables import PLAYER_INFO, ROOM_ID, SESSION_ID
from dto.game_context_dto import GameContextDto
from dto.match_closure_dto import EndingReason
from dto.partial_player_info_dto import PartialPlayerInfoDto
from exceptions.custom_exception import CustomException
from exceptions.server_error import ServerError
from exceptions.unauthorized_error import UnauthorizedError
from exceptions.wrong_data_error import WrongDataError
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
    partial_player_info = PartialPlayerInfoDto(
        player_info.playerId, player_info.isPlayer1
    )

    if player_info is None:
        raise ValueError("Could not resolve player information")

    return jsonify(partial_player_info.to_dict()), 200


@play_bp.route("/play/game-context", methods=["POST"])
def confirm_ids():
    """
    This route is called when the client failed to retrieve the room id
    and player id from the usual routes.
    """
    errorMessage = "An error occured while trying to connect to your match"

    json_data: dict = request.get_json()

    mhu = None
    player_id = json_data.get("playerId")
    room_id = json_data.get("roomId")

    try:
        if any(
            value is None
            for value in [player_id, room_id, match_handler.get_unit(room_id)]
        ):
            (mhu, player_id) = _get_from_session()
        else:
            (mhu, player_id) = _get_from_given_info(player_id, room_id)

        player_info = mhu.get_player(player_id)
        return jsonify(GameContextDto(mhu.match_info, player_info).to_dict()), 200

    except Exception as ex:
        if isinstance(ex, CustomException):
            raise ex

        logger.error(f"An error occured while trying to fetch the game context : {ex}")
        raise ServerError(errorMessage, socket_connection_killer=True)


def _get_from_given_info(player_id: str, room_id: str):
    try:
        mhu = match_handler.get_unit(room_id)

        player_ids = [
            mhu.match_info.player1.playerId,
            mhu.match_info.player2.playerId,
        ]
        if player_id not in player_ids:
            error_msg = (
                f"The player id {player_id} does not exist in the room {room_id}"
            )
            logger.error(error_msg)
            raise ValueError(error_msg)
    except Exception:
        (mhu, player_id) = _get_from_session()

    return mhu, player_id


def _get_from_session():
    mhu = match_handler.get_unit_from_session_id(session[SESSION_ID])
    player_id = next(
        (
            player_ID
            for player_ID, sid in mhu.session_ids.items()
            if sid == session[SESSION_ID]
        ),
        None,
    )
    return (mhu, player_id)
