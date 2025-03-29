from enum import IntFlag


class CellState(IntFlag):
    """
    Symbolises a state that is attached to the cell.
    Core states are mutually exclusive so a cell can only have one at a time,
    while modifier states can be combined.
    """

    NONE = 0

    # region Core states (mutually exclusive)

    # A cell that was just spawned and shouldn't be able to move nor attack
    # until next turn
    FRESHLY_SPAWNED = 1 << 0

    # For idle cells only. Whenever you spawn on it, the player gets 1 mana point
    MANA_BUBBLE = 1 << 1

    CORE_STATES = FRESHLY_SPAWNED | MANA_BUBBLE

    # endregion

    # region Modifier states (can be combined)

    # The shield will cancel the next damage the cell will take
    # (if any) and will be removed afterwards
    SHIELDED = 1 << 8

    # The cell can move and attack twice this turn
    ACCELERATED = 1 << 9

    # endregion

    # region Methods

    def core_states_cleared(self):
        return self & ~CellState.CORE_STATES

    def with_core_state(self, new_core_state: "CellState"):
        if not new_core_state.is_core_state():
            raise ValueError(f"The given state {new_core_state} is not a core state")

        cleared_state = self & ~CellState.CORE_STATES
        return cleared_state | new_core_state

    def contains(self, state: "CellState"):
        return bool(self & state)

    def is_core_state(self):
        return bool(self & CellState.CORE_STATES)

    def with_modifier(self, modifier: "CellState") -> "CellState":
        if modifier.is_core_state():
            raise ValueError("Cannot add a core state as modifier")
        return self | modifier

    def remove_state(self, modifier: "CellState") -> "CellState":
        return self & ~modifier

    # endregion
