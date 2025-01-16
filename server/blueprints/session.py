import uuid

from flask import Blueprint, current_app, jsonify, request, session

from constants.session_variables import ROOM_ID, SESSION_ID
from dto.boolean_dto import BooleanDto
from middlewares.error_handler import handle_error
from server_gate import get_match_handler, get_session_cache_handler
from utils import session_utils

session_bp = Blueprint("session", __name__)
session_bp.register_error_handler(Exception, handle_error)


@session_bp.route("/session", methods=["GET"])
def index():
    if session.get(SESSION_ID) is None:
        session_id = f"session-{uuid.uuid4()}"
        session[SESSION_ID] = session_id
        get_session_cache_handler().create_cache_for_session(session_id)
        return jsonify({"message": "Session initiated"}), 200

    return "", 204


@session_bp.route("/session/is-in-match", methods=["GET"])
def is_in_match():
    room_id = session.get(ROOM_ID)
    if not room_id:
        return BooleanDto(False).to_dict(), 200

    current_app.logger.info(f"({request.remote_addr}) is in a match")
    match_handler = get_match_handler()
    match = match_handler.get_unit(room_id)
    if match is None:
        return BooleanDto(False).to_dict(), 200

    if match.is_ongoing():
        BooleanDto(True).to_dict(), 200
    else:
        BooleanDto(False).to_dict(), 200


@session_bp.route("/match-session", methods=["DELETE"])
def delete_match_session_data():
    session_utils.clear_match_info()
    return "", 204
