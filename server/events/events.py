from enum import Enum


class Events(Enum):

    QUEUE_REGISTER = "queue-register"
    QUEUE_REGISTERED = "queue-registered"
    QUEUE_WITHDRAWAL = "queue-withdrawal"
    MATCH_OPPONENT_FOUND = "match-opponentFound"
    MATCH_READY = "match-ready"
