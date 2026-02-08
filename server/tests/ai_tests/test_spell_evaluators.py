import pytest
from game_engine.models.spells.spell_id import SpellId
from ai.strategy.decision_makers.spell_decider import SpellDecider
from ai.strategy.evaluators.spells.base_spell_evaluator import BaseSpellEvaluator


def test_each_spell_has_its_own_evaluator(mock_match):
    """
    Ensures that every defined SpellId has a corresponding evaluator
    initialized in the SpellDecider.
    """
    ai_is_player1 = True
    spell_decider = SpellDecider(mock_match, ai_is_player1)

    # Check that each SpellId is in the evaluators dictionary
    for spell_id in SpellId:
        assert (
            spell_id in spell_decider._evaluators
        ), f"Spell {spell_id.name} is missing an evaluator in SpellDecider"

        # Check that it's a valid evaluator instance
        evaluator = spell_decider._evaluators[spell_id]
        assert isinstance(
            evaluator, BaseSpellEvaluator
        ), f"Evaluator for {spell_id.name} must inherit from BaseSpellEvaluator"


def test_spell_evaluators_differentiation(mock_match):
    """
    Ensures that different spells have different evaluator instances.
    """
    ai_is_player1 = True
    spell_decider = SpellDecider(mock_match, ai_is_player1)

    evaluators = spell_decider._evaluators

    # Ensure they aren't all the same class instance (except if intended)
    # Most should be unique classes
    evaluator_classes = {type(eval) for eval in evaluators.values()}
    assert len(evaluator_classes) == len(
        SpellId
    ), "Each spell should ideally have its own evaluator class"
