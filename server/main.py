from application import Application
from socket_app import SocketApp

# WARNING : always set the current working directory as this file's
# one before running it

app = Application(__name__)

server = SocketApp(app)

from events.queue_events import *

if __name__ == "__main__":
    server.run()
