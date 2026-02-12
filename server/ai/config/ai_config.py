"""
Configuration settings for AI behavior, difficulty levels, and tuning parameters.

Organized by decision-making domain for easy navigation and tuning.
"""

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


class TurnManagement:
    """AI turn timing and action limits."""

    MAX_ACTIONS_PER_TURN = 50  # Safety limit to prevent infinite loops
    TURN_STARTING_DELAY_IN_S = 2.5  # Delay before AI starts taking actions, to simulate "thinking" and allow client animations to complete.
    THINKING_DELAY_MIN_IN_S = 0.2
    THINKING_DELAY_MAX_IN_S = 0.6
    DELAY_IN_BETWEEN_CLICKS_IN_S = 0.3  # Delay between simulated clicks for multi-click actions (like attacks/movements)
    DELAY_BEFORE_PASSING_TURN_IN_S = (
        0.8  # Delay before passing turn after completing actions
    )


class HealthThresholds:
    """Master health thresholds for defensive behaviors."""

    CRITICAL = 4  # HP ≤ this triggers defensive mode
    SUICIDAL = 1  # HP = this means master will die from any damage


class SpawnWeights:
    """Decision weights for spawn placement (SpawnDecider)."""

    BASE_SCORE = 45.0
    DISTANCE_TO_ENEMY_MASTER = 1.5
    DISTANCE_TO_OWN_MASTER = 1.0
    PROXIMITY_TO_FRIENDLY_CELLS = -1.0  # Avoid over-clustering
    THREAT_BLOCKING = 4.0
    MANA_BUBBLE_BONUS = 80.0  # Very high priority - spawn directly on mana bubbles
    MASTER_DEFENSE_BONUS = 70.0  # Increased to prioritize barricading after escape


class MovementWeights:
    """Decision weights for cell movement (MovementDecider)."""

    BASE_SCORE = 5.0
    DISTANCE_TO_ENEMY_MASTER = 0.8
    DISTANCE_TO_OWN_MASTER = 0.5
    MANA_BUBBLE_BONUS = 110.0  # Critical priority - grab mana bubbles directly
    MANA_BUBBLE_NEIGHBOR_BONUS = (
        75.0  # Strong priority - position next to bubble to capture next turn
    )
    ARCHER_CREATION_BONUS = 30.0  # Bonus for creating archer opportunities
    ARCHER_RETREAT_FROM_ENEMIES = 2.0  # Archers favor distance from enemies
    ENEMY_ARCHER_NEIGHBOR_BONUS = 120.0  # Very high priority - moving next to enemy archer to kill it next turn beats ambush
    MASTER_ESCAPE_BONUS = 130.0  # Critical priority - master moves to safety after being freed
    DEFENSIVE_POSITIONING = 3.0  # Boost movement toward own master when critical


class AttackWeights:
    """Decision weights for attacking enemy cells (AttackDecider)."""

    BASE_ATTACK = 55.0
    ENEMY_MASTER = 150.0
    LETHAL_ON_MASTER = 50.0  # Stacks on top of ENEMY_MASTER → 200
    THREAT_DEFENSE = 20.0
    LOW_HP_BONUS = 10.0
    ARCHER_TARGET_BONUS = (
        65.0  # High priority - kill archers before they establish range dominance
    )
    SAFE_ATTACK_BONUS = 25.0  # Bonus for safe attacks (ranged archer or shielded)
    MASTER_RESCUE_BONUS = 140.0  # Critical priority - free a trapped critical master
    MASTER_RETALIATION_PENALTY = (
        -40.0
    )  # Penalty: master should avoid attacking non-masters (loses HP)
    CRITICAL_THREAT_DEFENSE = (
        40.0  # Bonus for defending threats when master is critical
    )


class SpellWeights:
    """Decision weights for spell casting (SpellDecider)."""

    # General spell casting
    STAMINA_RECOVERY = 60.0  # Very high priority when stamina is low
    MP_CONSERVATION_THRESHOLD = 7
    MP_CONSERVATION_BONUS = 5.0

    # Ambush spell
    AMBUSH_BASE = 20.0  # Low base - ambush only valuable in specific situations
    AMBUSH_EXTRA_SPAWN_BONUS = 60.0  # High bonus when we get +1 spawn
    AMBUSH_ARCHER_TARGET_BONUS = (
        95.0  # Very high bonus for targeting an archer directly
    )
    AMBUSH_MASTER_TARGET_BONUS = (
        90.0  # Massive bonus when targeting enemy master for pressure
    )
    AMBUSH_CRITICAL_HEALTH_BONUS = (
        50.0  # Extra bonus when targeting threats and master is critical
    )

    # Mine Trap spell
    MINE_TRAP_BASE = 25.0
    MINE_TRAP_OWN_MASTER_PROXIMITY_FACTOR = 3.0
    MINE_TRAP_ENEMY_CLUSTER_BONUS = 45.0

    # Archery Vow spell
    ARCHERY_VOW_BASE = (
        75.0  # Increased to ensure follow-through after archer creation moves
    )
    ARCHERY_VOW_FORWARD_POSITION_BONUS = 5.0
    ARCHERY_VOW_AVAILABILITY_BONUS = 20.0  # Bonus when spell is actually castable

    # Shield Formation spell
    SHIELD_FORMATION_BASE = 85.0  # High base due to strong defensive potential
    SHIELD_FORMATION_CRITICAL_BONUS = 30.0
    SHIELD_FORMATION_PER_CELL_BONUS = 10.0  # Bonus per non-shielded cell in square
    SHIELD_FORMATION_REDUNDANT_PENALTY = (
        10.0  # Penalty per already-shielded cell in square
    )

    # Celerity spell
    CELERITY_BASE = 45.0
    CELERITY_ADVANTAGE_BONUS = 25.0
    CELERITY_PER_CELL_BONUS = 8.0  # Bonus per cell in diagonal formation
    CELERITY_SPECIAL_CELL_BONUS = (
        15.0  # Bonus per special cell (archer/master/shielded)
    )
    CELERITY_REDUNDANT_PENALTY = (
        12.0  # Penalty per already-accelerated cell in diagonal
    )


class EvaluationConstants:
    """Constants used across board and threat evaluation."""

    MAX_BOARD_DISTANCE = 20  # Approximate max Manhattan distance on 11x11 board
    DEFENSIVE_SPAWN_THREAT_THRESHOLD = 3
    DEFENSIVE_MOVE_THREAT_THRESHOLD = 4
