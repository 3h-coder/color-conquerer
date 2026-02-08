from typing import TYPE_CHECKING
from ai.strategy.evaluators.spells.base_spell_evaluator import BaseSpellEvaluator
from ai.config.ai_config import (
    SPELL_WEIGHT_SHIELD_FORMATION_BASE,
    SPELL_WEIGHT_SHIELD_FORMATION_CRITICAL_BONUS,
)

if TYPE_CHECKING:
    from game_engine.models.actions.spell_casting import SpellCasting
    from ai.strategy.evaluators.board.board_evaluation import BoardEvaluation


class ShieldFormationEvaluator(BaseSpellEvaluator):
    def evaluate_spell(
        self, action: "SpellCasting", board_evaluation: "BoardEvaluation"
    ) -> float:
        # Shield formation targets a 2x2 square (guaranteed by calculation logic)
        score = SPELL_WEIGHT_SHIELD_FORMATION_BASE

        # Bonus if we are losing or AI master is under threat
        if (
            board_evaluation.ai_master_in_critical_danger()
            or board_evaluation.ai_is_losing()
        ):
            score += SPELL_WEIGHT_SHIELD_FORMATION_CRITICAL_BONUS

        return score
