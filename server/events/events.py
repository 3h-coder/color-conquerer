from enum import Enum


class Events(Enum):

    QUEUE_REGISTER = "queue-register"
    QUEUE_REGISTERED = "queue-registered"
    QUEUE_WITHDRAWAL = "queue-withdrawal"
    QUEUE_OPPONENT_FOUND = "queue-opponentFound"
    MATCH_READY = "match-ready"
