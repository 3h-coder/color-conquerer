from flask import Flask
from flask_socketio import SocketIO


class SocketApp:
    """
    Socket server to handle real time updates between with the client.

    Docs : https://flask-socketio.readthedocs.io/en/latest/
    Simple chat app example : https://github.com/miguelgrinberg/Flask-SocketIO-Chat
    """

    def __init__(self, app: Flask):
        self.app = app
        self.socketio = SocketIO(app, cors_allowed_origins="*")

    def run(self, host="0.0.0.0", port=5000, debug=True, **kwargs):
        self.socketio.run(self.app, host=host, port=port, debug=debug, **kwargs)
