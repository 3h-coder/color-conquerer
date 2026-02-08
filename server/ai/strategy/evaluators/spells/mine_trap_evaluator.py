from typing import TYPE_CHECKING, List
from ai.strategy.evaluators.spells.base_spell_evaluator import BaseSpellEvaluator
from game_engine.models.cell.cell_owner import CellOwner
from utils.board_utils import manhattan_distance, get_neighbours
from ai.config.ai_config import (
    SPELL_WEIGHT_MINE_TRAP_BASE,
    SPELL_WEIGHT_MINE_TRAP_OWN_MASTER_PROXIMITY_FACTOR,
    SPELL_WEIGHT_MINE_TRAP_ENEMY_CLUSTER_BONUS,
)

if TYPE_CHECKING:
    from game_engine.models.actions.spell_casting import SpellCasting
    from ai.strategy.evaluators.board.board_evaluation import BoardEvaluation
    from game_engine.models.cell.cell import Cell


class MineTrapEvaluator(BaseSpellEvaluator):
    # Turn thresholds for game-phase awareness
    EARLY_GAME_TURN_THRESHOLD = 5  # Before this turn, mines are wasteful

    def evaluate_spell(
        self, action: "SpellCasting", board_evaluation: "BoardEvaluation"
    ) -> float:
        # Early game penalty: mines are wasteful when no enemies are nearby
        if board_evaluation.current_turn < self.EARLY_GAME_TURN_THRESHOLD:
            return 2.0  # Very low score - prefer spawning instead

        score = SPELL_WEIGHT_MINE_TRAP_BASE
        target_coords = action.metadata.impacted_coords

        # Better if near our own master (defense)
        dist_to_ai = manhattan_distance(
            target_coords.row_index,
            target_coords.column_index,
            board_evaluation.ai_master_coords.row_index,
            board_evaluation.ai_master_coords.column_index,
        )
        score += max(
            0, (5 - dist_to_ai) * SPELL_WEIGHT_MINE_TRAP_OWN_MASTER_PROXIMITY_FACTOR
        )

        # Nuke potential: bonus if adjacent to many enemy cells or an enemy cluster
        neighbors: List["Cell"] = get_neighbours(
            target_coords.row_index,
            target_coords.column_index,
            self._match_context.game_board.board,
        )
        enemy_neighbors = [
            n
            for n in neighbors
            if n.owner != CellOwner.NONE
            and (n.owner == CellOwner.PLAYER_1) != self._ai_is_player1
        ]

        if enemy_neighbors:
            score += len(enemy_neighbors) * 2.0
            # Check if any of these neighbors belong to a large cluster
            for cluster in board_evaluation.enemy_cell_clusters:
                if len(cluster) >= 3 and any(n in cluster for n in enemy_neighbors):
                    score += SPELL_WEIGHT_MINE_TRAP_ENEMY_CLUSTER_BONUS
                    break

        return score
