from typing import TYPE_CHECKING

from constants.game_constants import DEFAULT_SPELL_ORIGINAL_COUNT
from dto.coordinates_dto import CoordinatesDto
from dto.partial_spell_dto import PartialSpellDto
from dto.spell_dto import SpellDto
from game_engine.models.cell.cell_owner import CellOwner
from game_engine.models.spells.spell_id import SpellId

if TYPE_CHECKING:
    from game_engine.models.cell.cell import Cell
    from game_engine.models.game_board import GameBoard


class Spell:
    """
    Base class for all spells.
    """

    ORIGINAL_COUNT = DEFAULT_SPELL_ORIGINAL_COUNT

    def __init__(self, id: SpellId, name: str, description: str, mana_cost: int):
        self.id = id
        self.name = name
        self.description = description
        self.mana_cost = mana_cost

    def to_dto(self, count: int):
        return SpellDto(
            id=self.id,
            name=self.name,
            description=self.description,
            manaCost=self.mana_cost,
            count=count,
            maxCount=self.ORIGINAL_COUNT,
        )

    def to_partial_dto(self):
        return PartialSpellDto(
            id=self.id,
            name=self.name,
            description=self.description,
            manaCost=self.mana_cost,
        )

    def get_possible_targets(self, board: "GameBoard") -> list["Cell"]:
        raise NotImplementedError

    def invoke(
        self, coordinates: CoordinatesDto, board: "GameBoard", invocator: CellOwner
    ):
        raise NotImplementedError
