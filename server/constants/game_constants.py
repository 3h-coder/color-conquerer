"""
Numeric values related to the game engine/rules and mechanics
that should not be manually configured but set only in the code.
"""

from game_engine.models.cell.cell_state import CellState
from game_engine.models.spells.spell_id import SpellId

# The number of rows and columns the board has
BOARD_SIZE = 11  # Do not ever change that
PLAYER_1_ROWS = (0, 4)  # Do not ever change that
PLAYER_2_ROWS = (6, 10)  # Do not ever change that

MAX_HP_VALUE = 12
MAX_MP_VALUE = 9
MAX_STAMINA_VALUE = 20

# The default number of copies of each spell in the deck.
DEFAULT_SPELL_ORIGINAL_COUNT = 5

SPELLS_MANA_COST = {
    SpellId.MINE_TRAP: 1,
    SpellId.CELERITY: 2,
    SpellId.AMBUSH: 2,
    SpellId.ARCHERY_VOW: 3,
    SpellId.SHIELD_FORMATION: 3,
}

# Combat mechanics
DAMAGE_PER_ATTACK = 1  # Each attack deals 1 HP damage to the target

# States that do no persist beyond a single turn

STATES_TO_CLEAR_AT_TURN_BEGINNING = [CellState.FRESHLY_SPAWNED]

STATES_TO_CLEAR_AT_TURN_END = [CellState.ACCELERATED]
