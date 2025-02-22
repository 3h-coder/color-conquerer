from game_engine.models.spells.mine_trap_spell import MineTrapSpell
from game_engine.models.spells.spell import Spell
from game_engine.models.spells.spell_id import SpellId

_SPELLS = {
    MineTrapSpell.ID: lambda: MineTrapSpell(),
}


def get_spell(spell_id: int) -> Spell:
    """
    Returns a spell instance associated with the given id.
    """
    return _SPELLS[spell_id]()


def get_initial_spell_deck():
    # TODO : fill with other spells
    return {SpellId.MINE_TRAP: 5}
