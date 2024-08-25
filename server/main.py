from application import Application
from server import Server

# WARNING : always set the current working directory as this file's
# one before running it

app = Application(__name__)
server = Server(app)

if __name__ == "__main__":
    server.start_polling_workers()
    server.run()
