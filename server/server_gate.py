"""
Module used to store the server instance so external modules can access it without importing main.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from server import Server

_server: "Server" = None


def set_server(server_ref: "Server"):
    global _server
    _server = server_ref


def get_server():
    return _server


def get_connection_handler():
    return None if _server is None else _server.connection_handler


def get_room_handler():
    return None if _server is None else _server.room_handler


def get_session_cache_handler():
    return None if _server is None else _server.session_cache_handler
