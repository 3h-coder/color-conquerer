from enum import StrEnum


class CancellationReason(StrEnum):
    SERVER_ERROR = "server error"
    BOTH_PLAYERS_NEVER_JOINED = "both players never joined"
    PLAYER_NEVER_JOINED = "player never joined"
