from game_engine.models.actions.action import Action
from game_engine.models.spells.spell_id import Spell_ID


class SpellCasting(Action):
    """
    Represents the effective invocation of a spell.
    """

    spell_id: Spell_ID
