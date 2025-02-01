from game_engine.spells.mine_trap_spell import MineTrapSpell
from game_engine.spells.spell_base import SpellBase
from game_engine.spells.spell_id import Spell_ID

SPELLS = {
    Spell_ID.MINE_TRAP: lambda: MineTrapSpell(),
}


def get_spell(spell_id: int) -> SpellBase:
    """
    Returns the spell instance associated with the given id.
    """
    return SPELLS[spell_id]()
