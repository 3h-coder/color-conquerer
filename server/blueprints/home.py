from flask import Blueprint

from middlewares.error_handler import handle_error

home_bp = Blueprint("home", __name__)
home_bp.register_error_handler(Exception, handle_error)


@home_bp.route("/", methods=["GET", "POST"])
def index():
    pass
