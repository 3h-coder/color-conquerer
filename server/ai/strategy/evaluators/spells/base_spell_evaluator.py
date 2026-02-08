from typing import TYPE_CHECKING
from ai.strategy.evaluators.base_evaluator import BaseEvaluator

if TYPE_CHECKING:
    from game_engine.models.actions.spell_casting import SpellCasting
    from ai.strategy.evaluators.board.board_evaluation import BoardEvaluation


class BaseSpellEvaluator(BaseEvaluator):
    """
    Base class for all spell-specific evaluators.
    """

    def evaluate_spell(
        self, action: "SpellCasting", board_evaluation: "BoardEvaluation"
    ) -> float:
        """
        Calculates a score for a specific spell casting action.
        To be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement evaluate_spell")
