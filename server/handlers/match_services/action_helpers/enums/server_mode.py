from enum import IntEnum


class ServerMode(IntEnum):
    # The server intends to show the possible actions to the player whose turn it is
    SHOW_POSSIBLE_ACTIONS = 0
    # The server intends to show the processed action to both players
    SHOW_PROCESSED_ACTION = 1
    # The server intends to show the processed action and the resulting possible actions from it simultaneously
    # (example: all possible spawns after spawning a new cell)
    SHOW_PROCESSED_AND_POSSIBLE_ACTIONS = 2
