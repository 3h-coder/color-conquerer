import traceback

from flask import Flask
from flask_socketio import SocketIO, emit

from config.logging import get_configured_logger
from dto.server_only.error_dto import ErrorDto
from events import (
    handle_client_ready,
    handle_connection,
    handle_disconnection,
    handle_queue_registration,
    handle_session_clearing,
    handler_cell_hover,
    handler_cell_hover_end,
)
from events.events import Events
from exceptions.custom_exception import CustomException


class Server:
    """
    Socket server wrapper around a flask application to handle real time updates between with the client.

    Docs : https://flask-socketio.readthedocs.io/en/latest/
    Simple chat app example : https://github.com/miguelgrinberg/Flask-SocketIO-Chat
    Threading + Namespace example : https://github.com/miguelgrinberg/Flask-SocketIO/blob/main/example/app.py
    """

    def __init__(self, app: Flask):
        self.logger = get_configured_logger(__name__)
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
        self.socketio.on_event(Events.CLIENT_CELL_HOVER.value, handler_cell_hover)
        self.socketio.on_event(
            Events.CLIENT_CELL_HOVER_END.value, handler_cell_hover_end
        )
        self.socketio.on_event(
            Events.CLIENT_CLEAR_SESSION.value, handle_session_clearing
        )

        @self.socketio.on_error()
        def _(ex: Exception):
            if not isinstance(ex, CustomException):
                self.logger.error(f"A socket error occured : {traceback.format_exc()}")
            emit(Events.SERVER_ERROR.value, ErrorDto.from_exception(ex).to_dict())

    def run(self, host="0.0.0.0", port=5000, debug=True, **kwargs):
        self.socketio.run(
            self.app, host=host, port=port, debug=debug, use_reloader=False, **kwargs
        )
