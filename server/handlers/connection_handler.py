from flask import session

from config.logging import get_configured_logger
from constants.session_variables import SESSION_ID
from utils import session_utils


class ConnectionHandler:
    """
    Class responsible for tracking all of the user socket connections.
    """

    def __init__(self):
        self.logger = get_configured_logger(__name__)
        self.connections: dict[str, int] = {}

    def register_connection(self, remote_addr):
        if not session_utils.session_initialized():
            self.logger.warning(
                f"({remote_addr}) | Cannot register a connection in a non initialized session."
            )
            return

        if self.no_connection():
            self.connections[session[SESSION_ID]] = 1
        else:
            self.connections[session[SESSION_ID]] += 1

        self.logger.debug(
            f"({remote_addr}) | Socket Connection | Active connections -> {self.connections[session[SESSION_ID]]}"
        )

    def register_disconnection(self, remote_addr):
        if self.no_connection():
            return

        self.connections[session[SESSION_ID]] -= 1

        self.logger.debug(
            f"({remote_addr}) | Socket Disconnection | Active connections -> {self.connections[session[SESSION_ID]]}"
        )
        if self.connections[session[SESSION_ID]] == 0:
            del self.connections[session[SESSION_ID]]

    def no_connection(self):
        return (
            not session_utils.session_initialized()
            or session[SESSION_ID] not in self.connections
        )

    def single_connection(self):
        return not self.no_connection() and self.connections[session[SESSION_ID]] == 1
