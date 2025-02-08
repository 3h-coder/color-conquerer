from enum import IntEnum


class ActionType(IntEnum):
    CELL_MOVE = 0
    CELL_ATTACK = 1
    CELL_SPAWN = 2
    PLAYER_SPELL = 3
