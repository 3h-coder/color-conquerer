from dataclasses import dataclass
from dto.base_dto import BaseDto
from game_spells.spell_base import SpellBase


@dataclass
class SpellDto(BaseDto):
    id: int
    description: str
    manaCost: int
    count: int

    @staticmethod
    def from_spell(spell: SpellBase, count: int = 5):
        return SpellDto(
            id=spell.id,
            description=spell.description,
            manaCost=spell.mana_cost,
            count=count,
        )
