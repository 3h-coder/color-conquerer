"""
Configuration settings for AI behavior, difficulty levels, and tuning parameters.
"""

from dataclasses import dataclass


# TODO: Implement DifficultySettings (thinking delays, weights per difficulty level)
# when the AI logic is more mature.

# AI Turn Management
MAX_ACTIONS_PER_TURN = 50  # Safety limit to prevent infinite loops
TURN_STARTING_DELAY_IN_S = 2.5  # Delay before AI starts taking actions, to simulate "thinking" and allow client animations to complete.
THINKING_DELAY_MIN_IN_S = 0.2
THINKING_DELAY_MAX_IN_S = 0.6
DELAY_IN_BETWEEN_CLICKS_IN_S = 0.3  # Delay between simulated clicks for multi-click actions (like attacks/movements)
DELAY_BEFORE_PASSING_TURN_IN_S = (
    0.8  # Delay before passing turn after completing actions
)

# ===========================================================================
# All action scores are on a unified 0-200 scale so different action types
# (attack, spell, spawn, movement) compete fairly in the decision brain.
#
#   180-200  Game-ending (lethal on master)
#   120-170  Critical (master attack, key defensive spell)
#    60-100  Strong (good spell, mana bubble grab, threat near master)
#    30-60   Solid (regular attack, spawn, archery vow)
#    10-30   Filler (basic forward movement, low-value mine trap)
# ===========================================================================

# AI Decision Weights for SpawnDecider
SPAWN_WEIGHT_DISTANCE_TO_ENEMY_MASTER = 1.5
SPAWN_WEIGHT_DISTANCE_TO_OWN_MASTER = 1.0
SPAWN_WEIGHT_PROXIMITY_TO_FRIENDLY_CELLS = -1.0  # Avoid over-clustering
SPAWN_WEIGHT_THREAT_BLOCKING = 4.0
SPAWN_WEIGHT_MANA_BUBBLE_BONUS = (
    80.0  # Very high priority - spawn directly on mana bubbles
)

# AI Decision Weights for MovementDecider
MOVE_WEIGHT_DISTANCE_TO_ENEMY_MASTER = 0.8
MOVE_WEIGHT_DISTANCE_TO_OWN_MASTER = 0.5
BASE_MOVE_SCORE = 5.0
MOVE_WEIGHT_MANA_BUBBLE_BONUS = 110.0  # Critical priority - grab mana bubbles directly
MOVE_WEIGHT_MANA_BUBBLE_NEIGHBOR_BONUS = (
    75.0  # Strong priority - position next to bubble to capture next turn
)
MOVE_WEIGHT_ARCHER_CREATION_BONUS = 30.0  # Bonus for creating archer opportunities
MOVE_WEIGHT_ARCHER_RETREAT_FROM_ENEMIES = 2.0  # Archers favor distance from enemies
MOVE_WEIGHT_ENEMY_ARCHER_NEIGHBOR_BONUS = 120.0  # Very high priority - moving next to enemy archer to kill it next turn beats ambush

# AI Decision Weights for AttackDecider
ATTACK_WEIGHT_ENEMY_MASTER = 150.0
ATTACK_WEIGHT_LETHAL_ON_MASTER = 50.0  # Stacks on top of ENEMY_MASTER → 200
ATTACK_WEIGHT_BASE_ATTACK = 55.0
ATTACK_WEIGHT_THREAT_DEFENSE = 20.0
ATTACK_WEIGHT_LOW_HP_BONUS = 10.0
ATTACK_WEIGHT_ARCHER_TARGET_BONUS = (
    65.0  # High priority - kill archers before they establish range dominance
)
ATTACK_WEIGHT_MASTER_RETALIATION_PENALTY = (
    -40.0  # Penalty: master should avoid attacking non-masters (loses HP)
)
ATTACK_WEIGHT_CRITICAL_THREAT_DEFENSE = (
    40.0  # Bonus for defending threats when master is critical
)

# AI Decision Weights for MovementDecider - Defensive positioning
MOVE_WEIGHT_DEFENSIVE_POSITIONING = (
    3.0  # Boost movement toward own master when critical
)

# AI Decision Weights for SpawnDecider - Defensive positioning
SPAWN_WEIGHT_MASTER_DEFENSE_BONUS = (
    50.0  # Strong priority when master health is critical
)
MASTER_CRITICAL_HEALTH_THRESHOLD = 4  # HP ≤ this triggers defensive mode
MASTER_SUICIDAL_HEALTH_THRESHOLD = 1  # HP = this means master will die from any damage

# Evaluation Constants
BASE_SPAWN_SCORE = 45.0
MAX_BOARD_DISTANCE = 20  # Approximate max Manhattan distance on 11x11 board
DEFENSIVE_SPAWN_THREAT_THRESHOLD = 3
DEFENSIVE_MOVE_THREAT_THRESHOLD = 4

# AI Decision Weights for SpellDecider
SPELL_WEIGHT_STAMINA_RECOVERY = 60.0  # Very high priority when stamina is low
SPELL_WEIGHT_AMBUSH_BASE = (
    20.0  # Low base - ambush only valuable in specific situations
)
SPELL_WEIGHT_AMBUSH_EXTRA_SPAWN_BONUS = 60.0  # High bonus when we get +1 spawn
SPELL_WEIGHT_AMBUSH_ARCHER_TARGET_BONUS = (
    95.0  # Strong bonus for targeting an archer directly
)
SPELL_WEIGHT_AMBUSH_MASTER_TARGET_BONUS = (
    90.0  # Massive bonus when targeting enemy master for pressure
)
SPELL_WEIGHT_AMBUSH_CRITICAL_HEALTH_BONUS = (
    50.0  # Extra bonus when targeting threats and master is critical
)
SPELL_WEIGHT_MINE_TRAP_BASE = 25.0
SPELL_WEIGHT_MINE_TRAP_OWN_MASTER_PROXIMITY_FACTOR = 3.0
SPELL_WEIGHT_MINE_TRAP_ENEMY_CLUSTER_BONUS = 15.0
SPELL_WEIGHT_ARCHERY_VOW_BASE = (
    75.0  # Increased to ensure follow-through after archer creation moves
)
SPELL_WEIGHT_ARCHERY_VOW_FORWARD_POSITION_BONUS = 5.0
SPELL_WEIGHT_ARCHERY_VOW_AVAILABILITY_BONUS = (
    20.0  # Bonus when spell is actually castable
)
SPELL_WEIGHT_SHIELD_FORMATION_BASE = 65.0
SPELL_WEIGHT_SHIELD_FORMATION_CRITICAL_BONUS = 30.0
SPELL_WEIGHT_CELERITY_BASE = 45.0
SPELL_WEIGHT_CELERITY_ADVANTAGE_BONUS = 15.0
SPELL_WEIGHT_CELERITY_PER_CELL_BONUS = 8.0  # Bonus per cell in diagonal formation
SPELL_WEIGHT_CELERITY_SPECIAL_CELL_BONUS = (
    15.0  # Bonus per special cell (archer/master/shielded)
)
SPELL_WEIGHT_CELERITY_REDUNDANT_PENALTY = (
    50.0  # Penalty per already-accelerated cell in diagonal
)
SPELL_WEIGHT_SHIELD_FORMATION_REDUNDANT_PENALTY = (
    40.0  # Penalty per already-shielded cell in 2x2 square
)
SPELL_MP_CONSERVATION_THRESHOLD = 7
SPELL_MP_CONSERVATION_BONUS = 5.0
