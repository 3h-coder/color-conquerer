"""
BoardEvaluator - Analyzes the game board state to identify threats, opportunities, and strategic positions.

This evaluator provides comprehensive board analysis including:
- Cell control count (own vs enemy)
- Distance to enemy master
- Threats to own master
- Clustering opportunities (for AoE spells)
- Positional advantage
"""

from typing import TYPE_CHECKING
from collections import deque

from game_engine.models.cell.cell import Cell
from game_engine.models.game_board import GameBoard
from game_engine.models.dtos.coordinates import Coordinates
from ai.strategy.evaluators.board.board_evaluation import BoardEvaluation
from utils.board_utils import manhattan_distance
from ai.strategy.evaluators.base_evaluator import BaseEvaluator
from ai.strategy.evaluators.board.evaluation_constants import (
    THREAT_DETECTION_RANGE,
    THREAT_PER_ENEMY_CELL,
    MAX_BASE_THREAT_FROM_CELLS,
    MAX_THREAT_LEVEL,
    MIN_THREAT_LEVEL,
    CRITICAL_HP_THRESHOLD,
    LOW_HP_THRESHOLD,
    THREAT_INCREASE_CRITICAL_HP,
    THREAT_INCREASE_LOW_HP,
)
from utils.perf_utils import with_performance_logging

if TYPE_CHECKING:
    from handlers.match_handler_unit import MatchHandlerUnit


class BoardEvaluator(BaseEvaluator):
    """
    Evaluates the current board state to provide strategic insights for AI decision-making.
    """

    @with_performance_logging
    def evaluate(self) -> BoardEvaluation:
        """
        Performs a comprehensive evaluation of the current board state.

        Returns:
            BoardEvaluation object with all analysis results
        """
        game_board = self._match_context.game_board

        # Get AI and enemy player references
        ai_player = (
            self._match_context.player1
            if self._ai_is_player1
            else self._match_context.player2
        )
        enemy_player = (
            self._match_context.player2
            if self._ai_is_player1
            else self._match_context.player1
        )

        # Get all cells for both players
        ai_cells = game_board.get_cells_owned_by_player(player1=self._ai_is_player1)
        enemy_cells = game_board.get_cells_owned_by_player(
            player1=not self._ai_is_player1
        )

        # Find master cells
        ai_master_cell = self._find_master_cell(ai_cells)
        enemy_master_cell = self._find_master_cell(enemy_cells)

        # Cell control analysis
        ai_cell_count = len(ai_cells)
        enemy_cell_count = len(enemy_cells)
        cell_control_advantage = ai_cell_count - enemy_cell_count

        # Threat analysis
        enemy_cells_near_ai_master = self._find_cells_near_target(
            enemy_cells, ai_master_cell, max_distance=THREAT_DETECTION_RANGE
        )
        ai_cells_near_enemy_master = self._find_cells_near_target(
            ai_cells, enemy_master_cell, max_distance=THREAT_DETECTION_RANGE
        )

        # Calculate threat level considering both melee range and archers
        master_threat_level = self._calculate_threat_level(
            all_enemy_cells=enemy_cells,
            enemy_cells_near_master=enemy_cells_near_ai_master,
            target_hp=ai_player.resources.current_hp,
        )

        # Find all AI cells that can attack enemy master (including archers)
        ai_cells_that_can_attack_enemy_master = self._find_cells_that_can_attack_target(
            ai_cells, enemy_master_cell
        )

        # Positional analysis
        avg_ai_distance_to_enemy_master = self._calculate_average_distance_to_target(
            ai_cells, enemy_master_cell
        )
        avg_enemy_distance_to_ai_master = self._calculate_average_distance_to_target(
            enemy_cells, ai_master_cell
        )
        positional_advantage = (
            avg_enemy_distance_to_ai_master - avg_ai_distance_to_enemy_master
        )

        # Clustering analysis
        enemy_clusters = self._find_cell_clusters(enemy_cells, game_board)
        largest_cluster = max((len(cluster) for cluster in enemy_clusters), default=0)

        return BoardEvaluation(
            ai_cell_count=ai_cell_count,
            enemy_cell_count=enemy_cell_count,
            cell_control_advantage=cell_control_advantage,
            ai_master_cell=ai_master_cell,
            enemy_master_cell=enemy_master_cell,
            ai_master_coords=ai_master_cell.get_coordinates(),
            enemy_master_coords=enemy_master_cell.get_coordinates(),
            enemy_cells_near_ai_master=enemy_cells_near_ai_master,
            ai_cells_near_enemy_master=ai_cells_near_enemy_master,
            master_threat_level=master_threat_level,
            avg_ai_cell_distance_to_enemy_master=avg_ai_distance_to_enemy_master,
            avg_enemy_cell_distance_to_ai_master=avg_enemy_distance_to_ai_master,
            positional_advantage=positional_advantage,
            enemy_cell_clusters=enemy_clusters,
            largest_enemy_cluster_size=largest_cluster,
            ai_hp=ai_player.resources.current_hp,
            enemy_hp=enemy_player.resources.current_hp,
            ai_mp=ai_player.resources.current_mp,
            enemy_mp=enemy_player.resources.current_mp,
            ai_stamina=ai_player.resources.current_stamina,
            enemy_stamina=enemy_player.resources.current_stamina,
            ai_cells_that_can_attack_enemy_master=ai_cells_that_can_attack_enemy_master,
        )

    def _find_master_cell(self, cells: list[Cell]) -> Cell:
        """Finds and returns the master cell from a list of cells."""
        for cell in cells:
            if cell.is_master:
                return cell
        raise ValueError("No master cell found in the provided list")

    def _find_cells_near_target(
        self, cells: list[Cell], target: Cell, max_distance: int
    ) -> list[Cell]:
        """
        Finds all cells within a certain distance of a target cell.
        Uses Manhattan distance.
        """
        target_coords = target.get_coordinates()
        nearby_cells = []

        for cell in cells:
            if cell.is_master:
                continue  # Skip master cells in threat calculations

            cell_coords = cell.get_coordinates()
            distance = manhattan_distance(
                cell_coords.row_index,
                cell_coords.column_index,
                target_coords.row_index,
                target_coords.column_index,
            )
            if distance <= max_distance:
                nearby_cells.append(cell)

        return nearby_cells

    def _calculate_threat_level(
        self,
        all_enemy_cells: list[Cell],
        enemy_cells_near_master: list[Cell],
        target_hp: int,
    ) -> int:
        """
        Calculates a threat level from 0-10 based on enemy cells and HP.

        Considers both melee-range enemies and archers that can attack from anywhere.

        Higher threat means more danger to the target.
        """
        # Count archer cells anywhere on the board (they can attack from any distance)
        archer_cells = [
            cell for cell in all_enemy_cells if cell.is_archer() and not cell.is_master
        ]

        # Melee cells are only threatening if they're close
        melee_threatening_cells = [
            cell for cell in enemy_cells_near_master if not cell.is_archer()
        ]

        total_threatening_cells = len(melee_threatening_cells) + len(archer_cells)

        if total_threatening_cells == 0:
            return MIN_THREAT_LEVEL

        # Base threat on number of enemies that can attack
        threat = min(
            total_threatening_cells * THREAT_PER_ENEMY_CELL, MAX_BASE_THREAT_FROM_CELLS
        )

        # Increase threat if HP is low
        if target_hp <= CRITICAL_HP_THRESHOLD:
            threat += THREAT_INCREASE_CRITICAL_HP
        elif target_hp <= LOW_HP_THRESHOLD:
            threat += THREAT_INCREASE_LOW_HP

        return min(threat, MAX_THREAT_LEVEL)

    def _calculate_average_distance_to_target(
        self, cells: list[Cell], target: Cell
    ) -> float:
        """
        Calculates the average Manhattan distance from all cells to a target.
        """
        if not cells:
            return float("inf")

        target_coords = target.get_coordinates()
        total_distance = 0

        for cell in cells:
            if cell.is_master:
                continue  # Don't include master in average
            cell_coords = cell.get_coordinates()
            distance = manhattan_distance(
                cell_coords.row_index,
                cell_coords.column_index,
                target_coords.row_index,
                target_coords.column_index,
            )
            total_distance += distance

        # Subtract 1 to account for master cell we skipped
        cell_count = len(cells) - 1
        return total_distance / cell_count if cell_count > 0 else float("inf")

    def _find_cells_that_can_attack_target(
        self, cells: list[Cell], target: Cell
    ) -> list[Cell]:
        """
        Finds all cells that can attack the target.
        - Archer cells can attack from anywhere
        - Non-archer cells must be adjacent (within melee range)
        - Master cells can attack but lose HP in the process (decision layer should consider this risk)
        """
        cells_that_can_attack = []

        for cell in cells:
            if cell.is_archer():
                # Archers can attack from anywhere
                cells_that_can_attack.append(cell)
            else:
                # Non-archers must be adjacent
                cell_coords = cell.get_coordinates()
                target_coords = target.get_coordinates()
                distance = manhattan_distance(
                    cell_coords.row_index,
                    cell_coords.column_index,
                    target_coords.row_index,
                    target_coords.column_index,
                )
                # TODO : count in the movement ?
                if distance == 1:  # Adjacent cells only
                    cells_that_can_attack.append(cell)

        return cells_that_can_attack

    def _find_cell_clusters(
        self, cells: list[Cell], game_board: GameBoard
    ) -> list[list[Cell]]:
        """
        Identifies clusters of adjacent cells (useful for AoE spell targeting).

        Returns a list of cell clusters, where each cluster is a list of adjacent cells.
        """
        visited = set()
        clusters = []

        for cell in cells:
            if cell.id in visited or cell.is_master:
                continue

            # Start a new cluster with BFS
            cluster = []
            queue = deque([cell])

            while queue:
                current = queue.popleft()

                if current.id in visited:
                    continue

                visited.add(current.id)
                cluster.append(current)

                # Check all neighbors
                neighbors = game_board.get_neighbours(
                    current.row_index, current.column_index
                )

                for neighbor in neighbors:
                    if (
                        neighbor.id not in visited
                        and neighbor in cells
                        and not neighbor.is_master
                    ):
                        queue.append(neighbor)

            if len(cluster) > 0:
                clusters.append(cluster)

        return clusters
