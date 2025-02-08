from dataclasses import dataclass

from dto.base_dto import BaseDto


@dataclass
class SpellDto(BaseDto):
    id: int
    name: str
    description: str
    manaCost: int
    count: int
    maxCount: int
