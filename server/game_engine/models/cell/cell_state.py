from enum import IntEnum


class CellState(IntEnum):
    NONE = 0
    # A cell that was just spawned and shouldn't be able to move nor attack
    FRESHLY_SPAWNED = 1
    # For idle cells, whenever you spawn on it, the player gets 1 mana point
    MANA_BUBBLE = 2
    # Will explode when spwaned upon or moved into
    MINE_TRAP = 3
