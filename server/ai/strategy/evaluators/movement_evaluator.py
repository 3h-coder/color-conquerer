from typing import TYPE_CHECKING
from game_engine.models.dtos.coordinates import Coordinates
from game_engine.models.spells.spell_id import SpellId
from utils.board_utils import manhattan_distance
from ai.config.ai_config import (
    MOVE_WEIGHT_DISTANCE_TO_ENEMY_MASTER,
    MOVE_WEIGHT_DISTANCE_TO_OWN_MASTER,
    BASE_MOVE_SCORE,
    MAX_BOARD_DISTANCE,
    DEFENSIVE_MOVE_THREAT_THRESHOLD,
    MOVE_WEIGHT_MANA_BUBBLE_BONUS,
    MOVE_WEIGHT_MANA_BUBBLE_NEIGHBOR_BONUS,
    MOVE_WEIGHT_ARCHER_CREATION_BONUS,
    MOVE_WEIGHT_ARCHER_RETREAT_FROM_ENEMIES,
    MOVE_WEIGHT_ENEMY_ARCHER_NEIGHBOR_BONUS,
    MOVE_WEIGHT_DEFENSIVE_POSITIONING,
)
from ai.strategy.evaluators.base_evaluator import BaseEvaluator

if TYPE_CHECKING:
    from ai.strategy.evaluators.board.board_evaluation import BoardEvaluation
    from game_engine.models.actions.cell_movement import CellMovement
    from game_engine.models.cell.cell import Cell


class MovementEvaluator(BaseEvaluator):
    """
    Evaluates potential movement destinations for strategic value.
    """

    def evaluate(
        self,
        movement: "CellMovement",
        board_evaluation: "BoardEvaluation",
    ) -> float:
        """
        Calculates a score for a movement action.
        Delegates to specialized methods for clean separation of concerns.
        """
        dest_coords = movement.metadata.impacted_coords
        source_coords = movement.metadata.originating_coords
        board = self._match_context.game_board
        source_cell = board.get(source_coords.row_index, source_coords.column_index)

        score = BASE_MOVE_SCORE

        # Archers have different positioning priorities than regular cells
        if source_cell.is_archer():
            score += self._evaluate_archer_positioning(dest_coords)
        else:
            score += self._evaluate_standard_positioning(dest_coords, board_evaluation)

        score += self._evaluate_mana_bubble_opportunity(dest_coords)
        score += self._evaluate_enemy_archer_positioning(dest_coords)
        score += self._evaluate_archer_creation_opportunity(source_coords, dest_coords)

        return score

    def _evaluate_standard_positioning(
        self, dest_coords: Coordinates, board_evaluation: "BoardEvaluation"
    ) -> float:
        """
        Standard positioning: move closer to enemy master for offensive pressure,
        or closer to own master if defensive positioning is needed.
        When master is at critical health, strongly prioritize defensive positioning.
        """
        score = 0.0

        # Check if master is at critical health
        master_is_critical = self._is_ai_master_critical_health()

        # Offensive pressure: closer to enemy master is better
        dist_to_enemy_master = manhattan_distance(
            dest_coords.row_index,
            dest_coords.column_index,
            board_evaluation.enemy_master_coords.row_index,
            board_evaluation.enemy_master_coords.column_index,
        )
        score += (
            MAX_BOARD_DISTANCE - dist_to_enemy_master
        ) * MOVE_WEIGHT_DISTANCE_TO_ENEMY_MASTER

        # Defensive positioning when master is threatened or at critical health
        if (
            board_evaluation.master_threat_level >= DEFENSIVE_MOVE_THREAT_THRESHOLD
            or master_is_critical
        ):
            dist_to_own = manhattan_distance(
                dest_coords.row_index,
                dest_coords.column_index,
                board_evaluation.ai_master_coords.row_index,
                board_evaluation.ai_master_coords.column_index,
            )
            score += (
                MAX_BOARD_DISTANCE - dist_to_own
            ) * MOVE_WEIGHT_DISTANCE_TO_OWN_MASTER

            # Extra boost when master is critical - urgently move toward master
            if master_is_critical:
                score += (
                    MAX_BOARD_DISTANCE - dist_to_own
                ) * MOVE_WEIGHT_DEFENSIVE_POSITIONING

        return score

    def _evaluate_archer_positioning(
        self,
        dest_coords: Coordinates,
    ) -> float:
        """
        Archer positioning: favor distance from enemy cells for ranged advantage.
        Archers benefit from staying away from enemies while maintaining range.
        """
        board = self._match_context.game_board

        # Get all enemy cells
        enemy_cells = board.get_cells_owned_by_player(not self._ai_is_player1)

        # Calculate distance to nearest enemy cell
        min_distance_to_enemy = MAX_BOARD_DISTANCE
        for cell in enemy_cells:
            dist = manhattan_distance(
                dest_coords.row_index,
                dest_coords.column_index,
                cell.row_index,
                cell.column_index,
            )
            min_distance_to_enemy = min(min_distance_to_enemy, dist)

        # Archers favor being further from enemies (higher distance = higher score)
        return min_distance_to_enemy * MOVE_WEIGHT_ARCHER_RETREAT_FROM_ENEMIES

    def _evaluate_mana_bubble_opportunity(self, dest_coords: Coordinates) -> float:
        """
        Evaluates mana bubble capture opportunities.
        Prioritizes direct capture or positioning adjacent for next-turn capture.
        """
        board = self._match_context.game_board
        dest_cell = board.get(dest_coords.row_index, dest_coords.column_index)

        # Direct capture: highest priority
        if dest_cell.is_mana_bubble():
            return MOVE_WEIGHT_MANA_BUBBLE_BONUS

        # Adjacent positioning: capture next turn
        dest_neighbors = board.get_idle_neighbours(
            dest_coords.row_index, dest_coords.column_index
        )
        if any(neighbor.is_mana_bubble() for neighbor in dest_neighbors):
            return MOVE_WEIGHT_MANA_BUBBLE_NEIGHBOR_BONUS

        return 0.0

    def _evaluate_enemy_archer_positioning(self, dest_coords: Coordinates) -> float:
        """
        Position next to enemy archers to set up for killing them next turn.
        """
        board = self._match_context.game_board
        dest_neighbors = board.get_neighbours(
            dest_coords.row_index, dest_coords.column_index
        )

        # Check if any neighbor is an enemy archer
        for neighbor in dest_neighbors:
            if neighbor.is_owned() and neighbor.is_archer():
                # Check if it's an enemy cell
                if neighbor.belongs_to_player_1() != self._ai_is_player1:
                    return MOVE_WEIGHT_ENEMY_ARCHER_NEIGHBOR_BONUS

        return 0.0

    def _evaluate_archer_creation_opportunity(
        self, source_coords: Coordinates, dest_coords: Coordinates
    ) -> float:
        """
        Evaluates if this move would create an opportunity for Archery Vow.
        Returns a bonus score if:
        - AI has Archery Vow available (count > 0)
        - AI has enough MP to cast it (>= 3)
        - The moving cell itself would become isolated, OR
        - Moving away would leave a neighboring friendly cell isolated
        """
        # Check if Archery Vow is available
        ai_player = (
            self._match_context.player1
            if self._ai_is_player1
            else self._match_context.player2
        )
        archery_vow_count = ai_player.resources.spells.get(SpellId.ARCHERY_VOW, 0)

        # Must have the spell and enough MP
        if archery_vow_count <= 0 or ai_player.resources.current_mp < 3:
            return 0.0

        board = self._match_context.game_board
        source_cell = board.get(source_coords.row_index, source_coords.column_index)

        # Can't use Archery Vow on master
        if source_cell.is_master:
            return 0.0

        # Check if the moving cell itself would become isolated at destination
        dest_owned_neighbors = board.get_owned_neighbours(
            dest_coords.row_index, dest_coords.column_index
        )
        if len(dest_owned_neighbors) == 0:
            # Moving to a position with no friendly neighbors = isolated = archer candidate
            return MOVE_WEIGHT_ARCHER_CREATION_BONUS

        # Check neighbors at source - would any become isolated after we leave?
        source_neighbors = board.get_owned_neighbours(
            source_coords.row_index, source_coords.column_index
        )

        for neighbor in source_neighbors:
            if neighbor.is_master:
                continue  # Can't use Archery Vow on master

            # Check if this neighbor is owned by AI
            is_ai_owned = neighbor.belongs_to_player_1() == self._ai_is_player1
            if not is_ai_owned:
                continue

            # Count how many owned neighbors this cell currently has
            neighbor_owned_neighbors = board.get_owned_neighbours(
                neighbor.row_index, neighbor.column_index
            )

            # If it has exactly 1 owned neighbor (which is the cell we're about to move),
            # moving away would isolate it - perfect for Archery Vow
            if len(neighbor_owned_neighbors) == 1:
                return MOVE_WEIGHT_ARCHER_CREATION_BONUS

        return 0.0
