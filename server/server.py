import traceback
from typing import Callable

from flask import Flask
from flask_socketio import SocketIO, emit

from config import config
from config.logging import get_configured_logger
from config.variables import RequiredVariables
from dto.misc.error_dto import ErrorDto
from events.connect import handle_connection
from events.disconnect import handle_disconnection
from events.events import Events
from events.match_events import (
    handle_cell_click,
    handle_client_ready,
    handle_match_concede,
    handle_spawn_button,
    handle_spell_button,
    handle_turn_end,
)
from events.queue_events import handle_queue_registration
from exceptions.custom_exception import CustomException
from exceptions.server_error import ServerError
from handlers.connection_handler import ConnectionHandler
from handlers.match_handler import MatchHandler
from handlers.room_handler import RoomHandler
from handlers.session_cache_handler import SessionCacheHandler
from server_gate import set_server


class Server:
    """
    Socket server wrapper around a flask application to handle real time updates with the client.

    Docs : https://flask-socketio.readthedocs.io/en/latest/
    Simple chat app example : https://github.com/miguelgrinberg/Flask-SocketIO-Chat
    Threading + Namespace example : https://github.com/miguelgrinberg/Flask-SocketIO/blob/main/example/app.py
    """

    def __init__(self, app: Flask):
        self.logger = get_configured_logger(__name__)

        self.app = app
        self.debug = app.debug
        self.testing = app.testing

        self.socketio = SocketIO(
            app,
            cors_allowed_origins=config.get(RequiredVariables.CORS_ALLOWED_ORIGINS),
            manage_session=False,
        )

        self.connection_handler = ConnectionHandler()
        self.match_handler = MatchHandler()
        self.room_handler = RoomHandler()
        self.session_cache_handler = SessionCacheHandler()

        self.event_listeners: dict[str, Callable] = {}
        self._add_event_listeners()

        # Allow the instance to be available everywhere
        set_server(self)

    def _add_event_listeners(self):
        self._add_listener("connect", handle_connection)
        self._add_listener("disconnect", handle_disconnection)
        self._add_listener(Events.CLIENT_QUEUE_REGISTER, handle_queue_registration)
        self._add_listener(Events.CLIENT_READY, handle_client_ready)
        self._add_listener(Events.CLIENT_TURN_END, handle_turn_end)
        self._add_listener(Events.CLIENT_MATCH_CONCEDE, handle_match_concede)
        self._add_listener(Events.CLIENT_CELL_CLICK, handle_cell_click)
        self._add_listener(Events.CLIENT_SPAWN_BUTTON, handle_spawn_button)
        self._add_listener(Events.CLIENT_SPELL_BUTTON, handle_spell_button)

        @self.socketio.on_error()
        def _(ex: Exception):
            is_custom = isinstance(ex, CustomException)
            if not is_custom:
                self.logger.error(f"[SOCKET ERROR] {traceback.format_exc()}")

            error = ex if is_custom else ServerError(socket_connection_killer=True)
            emit(
                Events.SERVER_ERROR,
                ErrorDto.from_exception(error).to_dict(),
                to=error.broadcast_to,
                broadcast=bool(error.broadcast_to),
            )

    def _add_listener(self, event_name: str, listener: Callable):
        self.socketio.on_event(event_name, listener)
        self.event_listeners[event_name] = listener

    def run(self, host="0.0.0.0", port=5000, **kwargs):
        self.socketio.run(
            app=self.app,
            host=host,
            port=port,
            debug=self.debug,
            use_reloader=False,
            **kwargs,
        )
