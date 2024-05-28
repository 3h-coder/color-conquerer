from Application import Application
from SocketApp import SocketApp

app = Application(__name__)
app.config["SECRET_KEY"] = "your_secret_key_here"

socket_app = SocketApp(app)

if __name__ == "__main__":
    socket_app.run()
