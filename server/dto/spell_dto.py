from dataclasses import dataclass

from dto.partial_spell_dto import PartialSpellDto


@dataclass
class SpellDto(PartialSpellDto):
    count: int
    maxCount: int
