from dataclasses import dataclass

from dto.base_dto import BaseDto
from dto.spell_dto import SpellDto


@dataclass
class SpellsDto(BaseDto):
    spells: list[SpellDto]
