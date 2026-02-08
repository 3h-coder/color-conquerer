from typing import TYPE_CHECKING
from ai.strategy.evaluators.spells.base_spell_evaluator import BaseSpellEvaluator
from utils.board_utils import manhattan_distance
from ai.config.ai_config import (
    SPELL_WEIGHT_ARCHERY_VOW_BASE,
    SPELL_WEIGHT_ARCHERY_VOW_FORWARD_POSITION_BONUS,
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
        score = SPELL_WEIGHT_ARCHERY_VOW_BASE
        target_coords = action.metadata.impacted_coords

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
