from dataclasses import dataclass

from dto.base_dto import BaseDto
from dto.spell.spell_dto import SpellDto


@dataclass
class PlayerResourcesDto(BaseDto):
    maxHP: int
    currentHP: int
    maxMP: int
    currentMP: int
    # Spells cannot be shared with the opponent and
    # have their own separate dto
