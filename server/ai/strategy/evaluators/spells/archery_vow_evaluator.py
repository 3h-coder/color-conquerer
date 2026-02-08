from typing import TYPE_CHECKING
from ai.strategy.evaluators.spells.base_spell_evaluator import BaseSpellEvaluator
from utils.board_utils import manhattan_distance
from ai.config.ai_config import (
    SPELL_WEIGHT_ARCHERY_VOW_BASE,
    SPELL_WEIGHT_ARCHERY_VOW_FORWARD_POSITION_BONUS,
    SPELL_WEIGHT_ARCHERY_VOW_AVAILABILITY_BONUS,
    MAX_BOARD_DISTANCE,
)

if TYPE_CHECKING:
    from game_engine.models.actions.spell_casting import SpellCasting
    from ai.strategy.evaluators.board.board_evaluation import BoardEvaluation


class ArcheryVowEvaluator(BaseSpellEvaluator):
    def evaluate_spell(
        self, action: "SpellCasting", board_evaluation: "BoardEvaluation"
    ) -> float:
        # Archery vow targets isolated cells (guaranteed by calculation logic)
        target_coords = action.metadata.impacted_coords
        board = self._match_context.game_board
        target_cell = board.get(target_coords.row_index, target_coords.column_index)

        # Don't cast on cells that are already archers (avoid wasting mana)
        if target_cell.is_archer():
            return 0.0

        score = SPELL_WEIGHT_ARCHERY_VOW_BASE

        # Significant bonus since the spell is actually castable (has valid targets)
        # This ensures we follow through after moves that create archer opportunities
        score += SPELL_WEIGHT_ARCHERY_VOW_AVAILABILITY_BONUS

        # Bonus if the isolated cell is in a forward position (offensive pressure)
        dist_to_enemy = manhattan_distance(
            target_coords.row_index,
            target_coords.column_index,
            board_evaluation.enemy_master_coords.row_index,
            board_evaluation.enemy_master_coords.column_index,
        )
        score += (
            max(0, (MAX_BOARD_DISTANCE - dist_to_enemy) * 0.5)
            + SPELL_WEIGHT_ARCHERY_VOW_FORWARD_POSITION_BONUS
        )

        return score
