import eventlet

eventlet.monkey_patch()

from application import Application
from server import Server
from utils import sys_utils

# WARNING : always set the current working directory as this file's
# one before running it

app = Application(__name__)
server = Server(app)
# Needs to be exposed for gunicorn to find it
socketio = server.socketio

if __name__ == "__main__" and server.debug:
    server.run(**sys_utils.get_kwargs())
