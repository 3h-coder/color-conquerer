"""
Configuration settings for AI behavior, difficulty levels, and tuning parameters.
"""

from dataclasses import dataclass


# when the AI logic is more mature.

# AI Decision Weights for SpawnDecider
SPAWN_WEIGHT_DISTANCE_TO_ENEMY_MASTER = 5.0
SPAWN_WEIGHT_DISTANCE_TO_OWN_MASTER = 3.0
SPAWN_WEIGHT_PROXIMITY_TO_FRIENDLY_CELLS = -1.0  # Avoid over-clustering
SPAWN_WEIGHT_THREAT_BLOCKING = 4.0

# Evaluation Constants
BASE_SPAWN_SCORE = 10.0
MAX_BOARD_DISTANCE = 20  # Approximate max Manhattan distance on 11x11 board
DEFENSIVE_SPAWN_THREAT_THRESHOLD = 3
