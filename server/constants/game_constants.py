"""
Numeric values related to the game engine/rules and mechanics
that should not be manually configured but set only in the code.
"""

# The number of rows and columns the board has
from game_engine.models.cell.cell_state import CellState

BOARD_SIZE = 11  # Do not ever change that

MAX_HP_VALUE = 12
MAX_MP_VALUE = 9

# The default number of copies of each spell in the deck.
DEFAULT_SPELL_ORIGINAL_COUNT = 5

# States that do no persist beyond a single turn

STATES_TO_CLEAR_AT_TURN_BEGINNING = [CellState.FRESHLY_SPAWNED]

STATES_TO_CLEAR_AT_TURN_END = [CellState.ACCELERATED]
