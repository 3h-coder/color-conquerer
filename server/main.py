from Application import Application
from SocketApp import SocketApp


def main():
    app = Application(__name__)
    socket_app = SocketApp(app)
    socket_app.run()


if __name__ == "__main__":
    main()
