import { EMPTY_STRING } from "../env";
import { capitalizeAndReplaceUnderscores } from "../utils/stringUtils";

// ⚠️ Must be in sync with the server-side enum
export enum CellState {
    NONE = 0,

    // Core states (mutually exclusive)
    FRESHLY_SPAWNED = 1 << 0,
    MANA_BUBBLE = 1 << 1,

    // Modifier states (can be combined)
    SHIELDED = 1 << 8,
    ACCELERATED = 1 << 9,
    ARCHER = 1 << 10,
}

// Computed constants
const CORE_STATES = CellState.FRESHLY_SPAWNED | CellState.MANA_BUBBLE;

const CellStateDescriptions: Record<string, string> = {
    [CellState.FRESHLY_SPAWNED]: "The cell will only be able to act next turn.",
    [CellState.SHIELDED]: "The next damage to the cell will be cancelled.",
    [CellState.ACCELERATED]: "Can move and attack twice this turn.",
    [CellState.ARCHER]: "Can attack from a distance.",
    // No description needed
    [CellState.NONE]: EMPTY_STRING,
    [CellState.MANA_BUBBLE]: EMPTY_STRING
};

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
    },

    // Get descriptions for active states
    getActiveStateDescriptions(state: CellState): string[] {
        return this.getActiveStates(state).map(activeState => {
            const stateName = capitalizeAndReplaceUnderscores(CellState[activeState]);
            const description = CellStateDescriptions[activeState];
            if (!description) return EMPTY_STRING;

            return `${stateName} : ${description}`;
        });
    },
};