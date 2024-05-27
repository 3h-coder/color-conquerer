from flask import Flask
from flask_socketio import SocketIO


class SocketApp:
    def __init__(self, app: Flask):
        self.app = app
        self.socketio = SocketIO(
            app, cors_allowed_origins="*", supports_credentials=True
        )

    def register_namespace(self, namespace):
        self.socketio.on_namespace(namespace)

    def run(self, host="0.0.0.0", port=5000, debug=True, **kwargs):
        self.socketio.run(self.app, host=host, port=port, debug=debug, **kwargs)
