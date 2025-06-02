import eventlet

eventlet.monkey_patch()

from application import Application
from utils import sys_utils

from server import Server

# WARNING : always set the current working directory as this file's
# one before running it

if __name__ == "__main__":
    app = Application(__name__)
    server = Server(app)
    # Note: this calls socketio.run which is a production ready server
    # See https://flask-socketio.readthedocs.io/en/latest/deployment.html
    server.run(**sys_utils.get_kwargs())
