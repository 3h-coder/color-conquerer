from typing import TYPE_CHECKING
from ai.strategy.evaluators.spells.base_spell_evaluator import BaseSpellEvaluator
from utils.board_utils import manhattan_distance
from ai.config.ai_config import (
    SPELL_WEIGHT_AMBUSH_BASE,
    SPELL_WEIGHT_AMBUSH_OPPONENT_SIDE_BONUS,
    SPELL_WEIGHT_AMBUSH_DISTANCE_TO_MASTER_FACTOR,
    MAX_BOARD_DISTANCE,
)

if TYPE_CHECKING:
    from game_engine.models.actions.spell_casting import SpellCasting
    from ai.strategy.evaluators.board.board_evaluation import BoardEvaluation


class AmbushEvaluator(BaseSpellEvaluator):
    def evaluate_spell(
        self, action: "SpellCasting", board_evaluation: "BoardEvaluation"
    ) -> float:
        score = SPELL_WEIGHT_AMBUSH_BASE
        target_coords = action.metadata.impacted_coords

        # Bonus if target is on opponent's side (provides +1 extra cell)
        if target_coords.is_on_player_side(of_player1=not self._ai_is_player1):
            score += SPELL_WEIGHT_AMBUSH_OPPONENT_SIDE_BONUS

        # Better if near enemy master (pressure)
        dist_to_enemy = manhattan_distance(
            target_coords.row_index,
            target_coords.column_index,
            board_evaluation.enemy_master_coords.row_index,
            board_evaluation.enemy_master_coords.column_index,
        )
        score += max(
            0,
            (MAX_BOARD_DISTANCE - dist_to_enemy)
            * SPELL_WEIGHT_AMBUSH_DISTANCE_TO_MASTER_FACTOR,
        )

        return score
