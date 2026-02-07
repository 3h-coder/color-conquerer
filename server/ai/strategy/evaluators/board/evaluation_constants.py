"""
Constants used for board evaluation and threat assessment in AI decision-making.
"""

from constants.game_constants import DAMAGE_PER_ATTACK

# Threat distance thresholds
# THREAT_DETECTION_RANGE represents the "danger zone" around the master cell where enemy units
# are considered threatening. Value of 2 means:
# - Cells 1 space away can attack immediately next turn
# - Cells 2 spaces away can move+attack or are positioning for assault
# - Creates early warning system for defensive AI responses
# - Balances between paranoia (too large) and reactivity (too small)
THREAT_DETECTION_RANGE = 2  # Manhattan distance to consider cells as threatening

# Threat level calculation weights
THREAT_PER_ENEMY_CELL = 1  # Base threat points per enemy cell that can attack
MAX_BASE_THREAT_FROM_CELLS = 6  # Cap on threat from number of cells alone
MAX_THREAT_LEVEL = 10  # Maximum possible threat level (0-10 scale)
MIN_THREAT_LEVEL = 0  # Minimum threat level

# HP thresholds for threat assessment
CRITICAL_HP_THRESHOLD = 3  # HP at or below this is critical danger
LOW_HP_THRESHOLD = 6  # HP at or below this is considered low

# Threat increases based on HP
THREAT_INCREASE_CRITICAL_HP = 4  # Threat bonus when HP is critical
THREAT_INCREASE_LOW_HP = 2  # Threat bonus when HP is low

# Threat bonus per archer (can attack from anywhere on board)
THREAT_BONUS_PER_ARCHER = 1

# Note: DAMAGE_PER_ATTACK is imported from constants.game_constants

# Board evaluation thresholds for is_winning()
WINNING_CELL_ADVANTAGE_THRESHOLD = 3  # Need this many more cells to be "winning"
WINNING_THREAT_THRESHOLD = 5  # Threat level must be below this to be "winning"

# Board evaluation thresholds for is_losing()
LOSING_CELL_DISADVANTAGE_THRESHOLD = -3  # This many fewer cells means "losing"
LOSING_HP_DISADVANTAGE_THRESHOLD = 3  # Enemy has this much more HP means trouble
LOSING_THREAT_THRESHOLD = 7  # Threat level above this means "losing"

# Lethal opportunity thresholds
# Removed LETHAL_OPPORTUNITY_HP_THRESHOLD - now calculated dynamically based on attack potential

# Critical danger thresholds
CRITICAL_DANGER_THREAT_THRESHOLD = 8  # Threat level for critical danger
CRITICAL_DANGER_MIN_ATTACKERS = 2  # Multiple attackers near master is critical
CRITICAL_DANGER_HP_THRESHOLD = (
    4  # Master HP at or below this with attackers is critical
)
