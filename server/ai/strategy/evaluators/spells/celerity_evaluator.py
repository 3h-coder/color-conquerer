from typing import TYPE_CHECKING
from ai.strategy.evaluators.spells.base_spell_evaluator import BaseSpellEvaluator
from ai.config.ai_config import (
    SPELL_WEIGHT_CELERITY_BASE,
    SPELL_WEIGHT_CELERITY_ADVANTAGE_BONUS,
)

if TYPE_CHECKING:
    from game_engine.models.actions.spell_casting import SpellCasting
    from ai.strategy.evaluators.board.board_evaluation import BoardEvaluation


class CelerityEvaluator(BaseSpellEvaluator):
    def evaluate_spell(
        self, action: "SpellCasting", board_evaluation: "BoardEvaluation"
    ) -> float:
        score = SPELL_WEIGHT_CELERITY_BASE
        # Bonus if we are already in a good position to press the advantage
        if board_evaluation.positional_advantage > 0:
            score += SPELL_WEIGHT_CELERITY_ADVANTAGE_BONUS

        return score
