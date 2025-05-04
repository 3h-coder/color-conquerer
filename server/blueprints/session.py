import uuid

from flask import Blueprint, jsonify, session

from middlewares.error_handler import handle_error
from server_gate import get_session_cache_handler
from session_management.session_variables import SESSION_ID

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
