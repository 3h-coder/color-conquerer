from constants.game_constants import DEFAULT_SPELL_ORIGINAL_COUNT
from game_engine.models.spells.abstract.spell import Spell
from game_engine.models.spells.ambush_spell import AmbushSpell
from game_engine.models.spells.archery_vow_spell import ArcheryVowSpell
from game_engine.models.spells.celerity_spell import CeleritySpell
from game_engine.models.spells.mine_trap_spell import MineTrapSpell
from game_engine.models.spells.shield_formation_spell import \
    ShieldFormationSpell
from game_engine.models.spells.spell_id import SpellId

_SPELLS = {
    MineTrapSpell.ID: lambda: MineTrapSpell(),
    ShieldFormationSpell.ID: lambda: ShieldFormationSpell(),
    CeleritySpell.ID: lambda: CeleritySpell(),
    ArcheryVowSpell.ID: lambda: ArcheryVowSpell(),
    AmbushSpell.ID: lambda: AmbushSpell(),
}


def get_spell(spell_id: int) -> Spell:
    """
    Returns a spell instance associated with the given id.
    """
    return _SPELLS[spell_id]()


def get_initial_spell_deck():
    spell_count = DEFAULT_SPELL_ORIGINAL_COUNT
    # ranked by mana cost (least expensive to most expensive)
    return {
        SpellId.MINE_TRAP: spell_count,
        SpellId.CELERITY: spell_count,
        SpellId.AMBUSH: spell_count,
        SpellId.ARCHERY_VOW: spell_count,
        SpellId.SHIELD_FORMATION: spell_count,
    }
