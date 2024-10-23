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


def get_server() -> "Server":
    return _server
