from dataclasses import dataclass

from dto.base_dto import BaseDto
from game_engine.spells.mine_trap_spell import MineTrapSpell
from game_engine.spells.spell import Spell


@dataclass
class SpellDto(BaseDto):
    id: int
    name: str
    description: str
    manaCost: int
    count: int
    maxCount: int

    @staticmethod
    def from_spell(spell: Spell, max_count: int):
        return SpellDto(
            id=spell.id,
            name=spell.name,
            description=spell.description,
            manaCost=spell.mana_cost,
            count=max_count,
            maxCount=max_count,
        )

    @staticmethod
    def get_initial_deck():
        return [SpellDto.from_spell(MineTrapSpell(), 5)]
