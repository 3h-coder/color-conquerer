from typing import TYPE_CHECKING

from dto.coordinates_dto import CoordinatesDto
from game_engine.spells.spell_id import Spell_ID

if TYPE_CHECKING:
    from game_engine.models.cell import Cell


class SpellBase:
    """
    Base class for all spells.
    """

    def __init__(self, id: Spell_ID, name: str, description: str, mana_cost: int):
        self.id = id
        self.name = name
        self.description = description
        self.mana_cost = mana_cost

    def get_possible_targets(self, board: list[list["Cell"]]) -> list["Cell"]:
        raise NotImplementedError

    def invoke(self, coordinates: CoordinatesDto, board: list[list["Cell"]]):
        raise NotImplementedError
