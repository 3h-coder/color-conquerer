import sys
import traceback

import werkzeug.exceptions
from flask import current_app, jsonify

from dto.misc.error_dto import ErrorDto
from exceptions.custom_exception import CustomException


def handle_error(ex: Exception):
    code = _get_status_code(ex)
    return jsonify(ErrorDto.from_exception(ex)), code


def _get_status_code(exception: Exception) -> int:
    """Returns the response status code associated to the given exception (between 400 and 500)"""

    if isinstance(exception, CustomException) or isinstance(
        exception, werkzeug.exceptions.HTTPException
    ):
        return exception.code

    traceback.print_exception(*sys.exc_info())
    current_app.logger.error("An unhandled exception occurred: ", exc_info=True)
    return 500
