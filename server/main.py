from application import Application
from manager import MultiProcessingManager
from server import Server

# WARNING : always set the current working directory as this file's
# one before running it

app = Application(__name__)
server = Server(app)

if __name__ == "__main__":
    # Initialize the multiprocessing manager
    MultiProcessingManager.get_instance()
    server.run()
