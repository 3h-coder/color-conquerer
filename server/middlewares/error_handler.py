import sys
import traceback

from flask import jsonify

from main import server


def handle_error(ex: Exception):
    code = get_status_code(ex)
    return jsonify(error=str(ex)), code


def get_status_code(exception: Exception) -> int:
    """Returns the response status code associated to the given exception (between 400 and 500)"""

    traceback.print_exception(*sys.exc_info())
    server.app.logger.error("An unhandled exception occurred:", exc_info=True)
    return 500
