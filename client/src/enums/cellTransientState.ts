// ⚠️ Must be in sync with the server-side enum
export enum CellTransientState {
    NONE = 0,
    SELECTED = 1,
    CAN_BE_MOVED_INTO = 2,
    CAN_BE_SPAWNED_INTO = 3,
    CAN_BE_ATTACKED = 4,
    CAN_BE_SPELL_TARGETTED = 5
}