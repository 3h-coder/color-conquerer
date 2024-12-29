export enum CellTransientState {
    NONE = 0,
    SELECTED = 1,
    CAN_BE_MOVED_INTO = 2,
    CAN_BE_SPAWNED_INTO = 3,
    CAN_BE_ATTACKED = 4
}

export enum CellState {
    NONE = 0,
    FRESHLY_SPAWNED = 1
}