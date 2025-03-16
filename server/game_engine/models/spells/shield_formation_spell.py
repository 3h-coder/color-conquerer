from game_engine.models.spells.spell import Spell
from game_engine.models.spells.spell_id import SpellId


class ShieldFormationSpell(Spell):
    ID = SpellId.SHIELD_FORMATION
    NAME = "Shield formation"
    DESCRIPTION = "Select a square cell formation to apply a shield " "to each."
    MANA_COST = 3
