import uuid

from flask import Blueprint, jsonify, session

from constants.session_variables import SESSION_ID
from middlewares.error_handler import handle_error
from utils import session_utils

session_bp = Blueprint("session", __name__)
session_bp.register_error_handler(Exception, handle_error)


@session_bp.route("/session", methods=["GET"])
def index():
    if session.get(SESSION_ID) is None:
        session[SESSION_ID] = f"session-{uuid.uuid4()}"
        return jsonify({"message": "Session initiated"}), 204

    return "", 204


@session_bp.route("/match-session", methods=["DELETE"])
def delete_match_session_data():
    session_utils.clear_match_info()
    return "", 204
