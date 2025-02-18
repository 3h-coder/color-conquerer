from enum import IntEnum


class CellHiddenState(IntEnum):
    """
    A hidden state is only visible for the player owning the cell.
    If no player owns the cell, then the hidden state is only visible server side.
    """

    NONE = 0
    # Will explode when spwaned upon or moved into
    MINE_TRAP = 1
