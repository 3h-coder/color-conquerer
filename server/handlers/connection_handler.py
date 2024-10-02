from flask import session

from config.logger import logger
from constants.session_variables import SESSION_ID


class ConnectionHandler:
    """
    Class responsible for tracking all of the user socket connections.
    """

    def __init__(self):
        self.connections: dict[str, int] = {}

    def register_connection(self, remote_addr):
        if self.no_connection():
            self.connections[session[SESSION_ID]] = 1
        else:
            self.connections[session[SESSION_ID]] += 1

        logger.debug(
            f"({remote_addr}) | Socket Connection | Active connections -> {self.connections[session[SESSION_ID]]}"
        )

    def register_disconnection(self, remote_addr):
        if self.no_connection():
            return

        self.connections[session[SESSION_ID]] -= 1

        logger.debug(
            f"({remote_addr}) | Socket Disconnection | Active connections -> {self.connections[session[SESSION_ID]]}"
        )
        if self.connections[session[SESSION_ID]] == 0:
            del self.connections[session[SESSION_ID]]

    def no_connection(self):
        return session[SESSION_ID] not in self.connections

    def single_connection(self):
        return not self.no_connection() and self.connections[session[SESSION_ID]] == 1
