from enum import IntEnum


class PlayerMode(IntEnum):
    """
    This enum is shared with the client and is used to determine the current mode of the player.
    """

    # Default, the player is expected to select a cell, spawn a cell, or select a spell
    IDLE = 0
    # The player just selected a cell of their own and is expected to perform an action from it (move or attack)
    OWN_CELL_SELECTED = 1
    # A spawn action is being awaited on an idle cell with no owner
    CELL_SPAWN = 2
    # The player selected a spell, an action is possible on any cell as this depends on the spell
    SPELL_SELECTED = 3
