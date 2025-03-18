export enum CellState {
    NONE = 0,

    // Core states (mutually exclusive)
    FRESHLY_SPAWNED = 1 << 0,
    MANA_BUBBLE = 1 << 1,
}

// Computed constants
const CORE_STATES = CellState.FRESHLY_SPAWNED | CellState.MANA_BUBBLE;

// Helper functions
export const CellStateUtils = {
    contains(state: CellState, stateToCheck: CellState): boolean {
        return Boolean(state & stateToCheck);
    },

    isCoreState(state: CellState): boolean {
        return Boolean(state & CORE_STATES);
    },

    // Helper to get a readable list of active states
    getActiveStates(state: CellState): CellState[] {
        return Object.values(CellState)
            .filter(value => typeof value === 'number')
            .map(value => value as CellState)
            .filter(value => state & value);
    }
};