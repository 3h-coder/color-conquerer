import traceback

from flask import Flask
from flask_socketio import SocketIO, emit

from config.logger import logger
from dto.error_dto import ErrorDto
from events import (
    handle_client_ready,
    handle_connection,
    handle_disconnection,
    handle_queue_registration,
)
from events.events import Events
from exceptions.custom_exception import CustomException
from handlers import match_handler


class Server:
    """
    Socket server wrapper around a flask application to handle real time updates between with the client.

    Docs : https://flask-socketio.readthedocs.io/en/latest/
    Simple chat app example : https://github.com/miguelgrinberg/Flask-SocketIO-Chat
    Threading + Namespace example : https://github.com/miguelgrinberg/Flask-SocketIO/blob/main/example/app.py
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
        self.socketio.on_event(Events.CLIENT_READY.value, handle_client_ready)

        @self.socketio.on_error()
        def _(ex: Exception):
            if not isinstance(ex, CustomException):
                logger.error(f"A socket error occured : {traceback.format_exc()}")
            emit(Events.SERVER_ERROR.value, ErrorDto.from_exception(ex).to_dict())

    def run(self, host="0.0.0.0", port=5000, debug=True, **kwargs):
        self.socketio.run(
            self.app, host=host, port=port, debug=debug, use_reloader=False, **kwargs
        )

    def start_polling_workers(self):
        """
        Calls the start_polling_workers method on all of the handlers.
        """
        logger.debug("Starting polling workers")
        match_handler.start_polling_workers()
