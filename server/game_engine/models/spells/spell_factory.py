from game_engine.models.spells.mine_trap_spell import MineTrapSpell
from game_engine.models.spells.spell import Spell
from game_engine.models.spells.spell_id import Spell_ID

_SPELLS = {
    Spell_ID.MINE_TRAP: lambda: MineTrapSpell(),
}


def get_spell(spell_id: int) -> Spell:
    """
    Returns the spell instance associated with the given id.
    """
    return _SPELLS[spell_id]()
