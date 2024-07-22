import sys

from flask import Flask
from flask_socketio import SocketIO

from dto.error_dto import ErrorDto
from events import *
from events.connect import handle_connection
from events.events import Events
from exceptions.custom_exception import CustomException


class Server:
    """
    Socket server wrapper around a flask application to handle real time updates between with the client.

    Docs : https://flask-socketio.readthedocs.io/en/latest/
    Simple chat app example : https://github.com/miguelgrinberg/Flask-SocketIO-Chat
    """

    def __init__(self, app: Flask):
        self.app = app
        # TODO: add the proper origins
        self.socketio = SocketIO(app, cors_allowed_origins="*", manage_session=False)
        self._add_listeners()

    def _add_listeners(self):
        self.socketio.on_event("connect", handle_connection)
        self.socketio.on_event("disconnect", handle_disconnection)
        self.socketio.on_event(
            Events.CLIENT_QUEUE_REGISTER.value, handle_queue_registration
        )

        @self.socketio.on_error()
        def _(ex: Exception):
            if not isinstance(ex, CustomException):
                logger.error(
                    f"A socket error occured : {ex.with_traceback(sys.exception().__traceback__)}"
                )
            emit(Events.SERVER_ERROR.value, ErrorDto.from_exception(ex))

    def run(self, host="0.0.0.0", port=5000, debug=True, **kwargs):
        self.socketio.run(self.app, host=host, port=port, debug=debug, **kwargs)
