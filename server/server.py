import subprocess
import traceback
from typing import Callable

from flask import Flask
from flask_socketio import SocketIO, emit

from config import TESTS_FOLDER_NAME, config
from config.logging import get_configured_logger
from config.variables import OptionalVariable, RequiredVariable
from dto.misc.error_dto import ErrorDto
from events.connect import handle_connection
from events.disconnect import handle_disconnection
from events.events import Events
from events.match_events import (handle_cell_click, handle_client_ready,
                                 handle_match_concede, handle_spawn_button,
                                 handle_spell_button, handle_turn_end)
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

    
        socketio_path = "socket.io" # default value
        # Must be the same as the one used in the frontend
        # Debug should be set to true during development
        path = f"/api/{socketio_path}/" if not self.debug and not self.testing else socketio_path

        self.socketio = SocketIO(
            app,
            cors_allowed_origins=config.get(RequiredVariable.CORS_ALLOWED_ORIGINS),
            manage_session=False,
            path=path
        )

        self.connection_handler = ConnectionHandler()
        self.match_handler = MatchHandler(server=self)
        self.room_handler = RoomHandler()

        # Do not enable that with redis sessions
        self.session_cache_handler = SessionCacheHandler(
            enabled=not config.get(RequiredVariable.APP_REDIS_SESSION_STORAGE)
        )

        self.event_listeners: dict[str, Callable] = {}
        self._add_event_listeners()

        # Allow the instance to be available everywhere
        set_server(self)

    def run(self, host="127.0.0.1", port=None, **kwargs):
        test_success = self._run_tests()
        if not test_success:
            self.logger.error("Tests failed, not starting the server.")
            return

        if port is None:
            port = config.get(RequiredVariable.BACKEND_SERVER_PORT)

        self.logger.info(f"Starting server on {host}:{port} with debug={self.debug}")
        self.socketio.run(
            app=self.app,
            host=host,
            port=port,
            debug=self.debug,
            use_reloader=False,
            **kwargs,
        )

        self.logger.info("\n===== Flask socketio server startup complete =====\n")

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

    def _run_tests(self) -> bool:
        """
        Run tests for the server.
        Returns:
            bool: True if all tests passed or were skipped, False otherwise.
        """
        if not config.get(OptionalVariable.RUN_TESTS_ON_STARTUP):
            self.logger.info("Skipping server tests as per configuration.")
            return True

        self.logger.info("Running server tests with pytest...")
        # Run pytest and stream output live to the console
        process = subprocess.Popen(
            ["pytest", TESTS_FOLDER_NAME],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        # Print each line as it comes
        output_lines = []
        for line in process.stdout:
            print(line, end="")
            output_lines.append(line)
        process.wait()

        self.logger.info(f"Pytest output:\n{"".join(output_lines)}")
        return process.returncode == 0
