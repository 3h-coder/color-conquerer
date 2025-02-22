export enum CellTransientState {
    NONE = 0,
    SELECTED = 1,
    CAN_BE_MOVED_INTO = 2,
    CAN_BE_SPAWNED_INTO = 3,
    CAN_BE_ATTACKED = 4,
    CAN_BE_SPELL_TARGETTED = 5
}

export enum CellState {
    NONE = 0,
    FRESHLY_SPAWNED = 1,
    MANA_BUBBLE = 2,
}

export enum CellHiddenState {
    NONE = 0,
    MINE_TRAP = 1
}