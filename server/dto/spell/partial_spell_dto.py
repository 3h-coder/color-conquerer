from dataclasses import dataclass

from dto.base_dto import BaseDto


@dataclass
class PartialSpellDto(BaseDto):
    id: int
    name: str
    description: str
    manaCost: int
