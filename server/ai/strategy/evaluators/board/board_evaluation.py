"""
BoardEvaluation - Data class containing the results of board state analysis.
"""

from dataclasses import dataclass

from ai.strategy.evaluators.board.evaluation_constants import (
    CRITICAL_DANGER_HP_THRESHOLD, CRITICAL_DANGER_MIN_ATTACKERS,
    CRITICAL_DANGER_THREAT_THRESHOLD, DAMAGE_PER_ATTACK,
    LOSING_CELL_DISADVANTAGE_THRESHOLD, LOSING_HP_DISADVANTAGE_THRESHOLD,
    LOSING_THREAT_THRESHOLD, WINNING_CELL_ADVANTAGE_THRESHOLD,
    WINNING_THREAT_THRESHOLD)
from game_engine.models.cell.cell import Cell
from game_engine.models.dtos.coordinates import Coordinates


@dataclass
class BoardEvaluation:
    """
    Container for the results of a board evaluation.

    This class holds comprehensive analysis of the current game state including
    cell control, threats, positioning, and resource comparisons.
    """

    # Cell control metrics
    ai_cell_count: int
    enemy_cell_count: int
    cell_control_advantage: int  # positive = AI advantage, negative = enemy advantage

    # Master cell information
    ai_master_cell: Cell
    enemy_master_cell: Cell
    ai_master_coords: Coordinates
    enemy_master_coords: Coordinates

    # Threat analysis
    enemy_cells_near_ai_master: list[Cell]  # Enemy cells that can threaten AI's master
    ai_cells_near_enemy_master: list[Cell]  # AI cells that can threaten enemy's master
    master_threat_level: int  # 0-10, how threatened is AI's master
    is_ai_master_stuck: bool  # True if AI master has no valid moves

    # Positioning metrics
    avg_ai_cell_distance_to_enemy_master: float
    avg_enemy_cell_distance_to_ai_master: float
    positional_advantage: (
        float  # positive = AI closer to enemy, negative = enemy closer to AI
    )

    # Clustering analysis (useful for AoE spells)
    enemy_cell_clusters: list[list[Cell]]  # Groups of adjacent enemy cells
    largest_enemy_cluster_size: int

    # Resource comparison
    ai_hp: int
    enemy_hp: int
    ai_mp: int
    enemy_mp: int
    ai_stamina: int
    enemy_stamina: int

    # Game phase context
    current_turn: int  # Turn number for game-phase awareness

    # Attack potential (for lethal calculations)
    ai_cells_that_can_attack_enemy_master: list[
        Cell
    ]  # All AI cells that can reach enemy master

    def ai_is_winning(self) -> bool:
        """Returns True if AI appears to be in a winning position."""
        return (
            self.cell_control_advantage > WINNING_CELL_ADVANTAGE_THRESHOLD
            and self.ai_hp > self.enemy_hp
            and self.master_threat_level < WINNING_THREAT_THRESHOLD
        )

    def ai_is_losing(self) -> bool:
        """Returns True if AI appears to be in a losing position."""
        return (
            self.cell_control_advantage < LOSING_CELL_DISADVANTAGE_THRESHOLD
            or self.ai_hp < self.enemy_hp - LOSING_HP_DISADVANTAGE_THRESHOLD
            or self.master_threat_level > LOSING_THREAT_THRESHOLD
        )

    def ai_has_lethal_opportunity(self) -> bool:
        """Returns True if AI can potentially kill enemy master this turn."""
        # Calculate maximum damage AI can deal this turn
        # Each cell can attack once, dealing 1 damage per attack
        max_damage_potential = (
            len(self.ai_cells_that_can_attack_enemy_master) * DAMAGE_PER_ATTACK
        )

        # AI has lethal if it can deal enough damage to kill the enemy master
        return max_damage_potential >= self.enemy_hp

    def ai_master_in_critical_danger(self) -> bool:
        """Returns True if AI's master is in immediate danger."""
        return self.master_threat_level >= CRITICAL_DANGER_THREAT_THRESHOLD or (
            len(self.enemy_cells_near_ai_master) >= CRITICAL_DANGER_MIN_ATTACKERS
            and self.ai_hp <= CRITICAL_DANGER_HP_THRESHOLD
        )

    def __str__(self) -> str:
        """Returns a human-readable string representation of the evaluation."""
        return (
            f"BoardEvaluation:\n"
            f"  Turn: {self.current_turn}\n"
            f"  Cell Control: AI={self.ai_cell_count}, Enemy={self.enemy_cell_count}, Advantage={self.cell_control_advantage:+d}\n"
            f"  Resources (ai-player): HP={self.ai_hp}-{self.enemy_hp}, MP={self.ai_mp}-{self.enemy_mp}, Stamina={self.ai_stamina}-{self.enemy_stamina}\n"
            f"  Threats: Master threat={self.master_threat_level}/10, Enemies near master={len(self.enemy_cells_near_ai_master)}\n"
            f"  Attack Potential: AI cells that can attack the enemy master={len(self.ai_cells_that_can_attack_enemy_master)}\n"
            f"  Positioning: Advantage={self.positional_advantage:.2f}, Avg distance to enemy={self.avg_ai_cell_distance_to_enemy_master:.2f}\n"
            f"  Clustering: Largest enemy cluster={self.largest_enemy_cluster_size}, Total clusters={len(self.enemy_cell_clusters)}\n"
            f"  Status Flags: Winning={self.ai_is_winning()}, Losing={self.ai_is_losing()}, Lethal={self.ai_has_lethal_opportunity()}, Critical Danger={self.ai_master_in_critical_danger()}"
        )
