from dataclasses import dataclass

from dto.base_dto import BaseDto
from dto.spell_dto import SpellDto


@dataclass
class PlayerResourcesDto(BaseDto):
    maxHP: int
    currentHP: int
    maxMP: int
    currentMP: int
    # WARNING : this value must be an empty list for the
    # player1 if sent to player2 and vice-versa
    spells: list[SpellDto]
