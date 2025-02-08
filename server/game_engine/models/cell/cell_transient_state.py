"""
The transient states are temporary and meant to be sent to
the player whose turn it is to inform him of the
possible actions he can take.
"""

from enum import IntEnum


class CellTransientState(IntEnum):
    NONE = 0
    SELECTED = 1
    CAN_BE_MOVED_INTO = 2
    CAN_BE_SPAWNED_INTO = 3
    CAN_BE_ATTACKED = 4
    CAN_BE_SPELL_TARGETTED = 5
