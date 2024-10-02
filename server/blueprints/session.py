import uuid

from flask import Blueprint, jsonify, session

from constants.session_variables import SESSION_ID
from exceptions.custom_exception import CustomException
from middlewares.error_handler import handle_error

session_bp = Blueprint("session", __name__)
session_bp.register_error_handler(Exception, handle_error)


@session_bp.route("/session", methods=["GET", "POST"])
def index():
    if session.get(SESSION_ID) is None:
        session[SESSION_ID] = f"session-{uuid.uuid4()}"
        return jsonify({"message": "Session initiated"}), 204

    return "", 204
