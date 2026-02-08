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

# AI Decision Weights for SpawnDecider
SPAWN_WEIGHT_DISTANCE_TO_ENEMY_MASTER = 5.0
SPAWN_WEIGHT_DISTANCE_TO_OWN_MASTER = 3.0
SPAWN_WEIGHT_PROXIMITY_TO_FRIENDLY_CELLS = -1.0  # Avoid over-clustering
SPAWN_WEIGHT_THREAT_BLOCKING = 4.0

# AI Decision Weights for MovementDecider
MOVE_WEIGHT_DISTANCE_TO_ENEMY_MASTER = 8.0
MOVE_WEIGHT_DISTANCE_TO_OWN_MASTER = 4.0
BASE_MOVE_SCORE = 5.0

# Evaluation Constants
BASE_SPAWN_SCORE = 10.0
MAX_BOARD_DISTANCE = 20  # Approximate max Manhattan distance on 11x11 board
DEFENSIVE_SPAWN_THREAT_THRESHOLD = 3
DEFENSIVE_MOVE_THREAT_THRESHOLD = 4
