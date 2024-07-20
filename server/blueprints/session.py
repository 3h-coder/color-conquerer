from flask import Blueprint, jsonify, session

from config.logger import logger
from exceptions.custom_exception import CustomException
from middlewares.error_handler import handle_error

session_bp = Blueprint("session", __name__)
session_bp.register_error_handler(Exception, handle_error)


@session_bp.route("/session", methods=["GET", "POST"])
def index():
    if session.get("initiated") is None:
        session["initiated"] = True
        return jsonify({"message": "Session initiated"}), 204

    return "", 200
