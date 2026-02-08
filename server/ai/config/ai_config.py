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

# AI Decision Weights for MovementDecider
MOVE_WEIGHT_DISTANCE_TO_ENEMY_MASTER = 0.8
MOVE_WEIGHT_DISTANCE_TO_OWN_MASTER = 0.5
BASE_MOVE_SCORE = 5.0

# AI Decision Weights for AttackDecider
ATTACK_WEIGHT_ENEMY_MASTER = 150.0
ATTACK_WEIGHT_LETHAL_ON_MASTER = 50.0  # Stacks on top of ENEMY_MASTER → 200
ATTACK_WEIGHT_BASE_ATTACK = 55.0
ATTACK_WEIGHT_THREAT_DEFENSE = 20.0
ATTACK_WEIGHT_LOW_HP_BONUS = 10.0

# Evaluation Constants
BASE_SPAWN_SCORE = 45.0
MAX_BOARD_DISTANCE = 20  # Approximate max Manhattan distance on 11x11 board
DEFENSIVE_SPAWN_THREAT_THRESHOLD = 3
DEFENSIVE_MOVE_THREAT_THRESHOLD = 4

# AI Decision Weights for SpellDecider
SPELL_WEIGHT_STAMINA_RECOVERY = 60.0  # Very high priority when stamina is low
SPELL_WEIGHT_AMBUSH_BASE = 70.0
SPELL_WEIGHT_AMBUSH_OPPONENT_SIDE_BONUS = 15.0
SPELL_WEIGHT_AMBUSH_DISTANCE_TO_MASTER_FACTOR = 0.5
SPELL_WEIGHT_MINE_TRAP_BASE = 25.0
SPELL_WEIGHT_MINE_TRAP_OWN_MASTER_PROXIMITY_FACTOR = 3.0
SPELL_WEIGHT_MINE_TRAP_ENEMY_CLUSTER_BONUS = 15.0
SPELL_WEIGHT_ARCHERY_VOW_BASE = 55.0
SPELL_WEIGHT_ARCHERY_VOW_FORWARD_POSITION_BONUS = 5.0
SPELL_WEIGHT_SHIELD_FORMATION_BASE = 65.0
SPELL_WEIGHT_SHIELD_FORMATION_CRITICAL_BONUS = 30.0
SPELL_WEIGHT_CELERITY_BASE = 45.0
SPELL_WEIGHT_CELERITY_ADVANTAGE_BONUS = 15.0
SPELL_MP_CONSERVATION_THRESHOLD = 7
SPELL_MP_CONSERVATION_BONUS = 5.0
