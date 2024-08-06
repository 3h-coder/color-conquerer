from enum import Enum


class Events(Enum):
    """
    Represents all the different socket events transmitted between the client and the server.

    The prefix (i.e. CLIENT or SERVER) indicates who sends the event (and therefore the other one listens to it)
    """

    SERVER_ERROR = "server-error"
    CLIENT_QUEUE_REGISTER = "queue-register"
    SERVER_QUEUE_REGISTERED = "queue-registered"
    SERVER_QUEUE_OPPONENT_FOUND = "queue-opponentFound"
    CLIENT_MATCH_INFO = "client-match-info"
    SERVER_MATCH_INFO = "server-match-info"
    CLIENT_READY = "client-ready"  # ready to start or resume a game
    SERVER_MATCH_OPPONENT_LEFT = "match-opponentLeft"
