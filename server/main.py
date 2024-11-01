from application import Application
from server import Server
from server_gate import set_server

# WARNING : always set the current working directory as this file's
# one before running it

if __name__ == "__main__":
    app = Application(__name__)
    server = Server(app)
    set_server(server)
    server.run()
