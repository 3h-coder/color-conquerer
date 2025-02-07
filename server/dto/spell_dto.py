from dataclasses import dataclass

from dto.base_dto import BaseDto
from game_engine.models.spells.mine_trap_spell import MineTrapSpell
from game_engine.models.spells.spell import Spell


@dataclass
class SpellDto(BaseDto):
    id: int
    name: str
    description: str
    manaCost: int
    count: int
    maxCount: int
