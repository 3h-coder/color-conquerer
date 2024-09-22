"""
Module used to store the server instance so external modules can access it without importing main.
"""

from server import Server

server: Server = None


def set_server(value: Server):
    global server
    server = value
