from typing import TYPE_CHECKING, Any

from constants.game_constants import DEFAULT_SPELL_ORIGINAL_COUNT
from dto.spell.partial_spell_dto import PartialSpellDto
from dto.spell.spell_dto import SpellDto
from game_engine.models.cell.cell_owner import CellOwner
from game_engine.models.coordinates import Coordinates
from game_engine.models.spells.spell_id import SpellId

if TYPE_CHECKING:
    from game_engine.models.cell.cell import Cell
    from game_engine.models.game_board import GameBoard


class Spell:
    """
    Base class for all spells.
    """

    ID = 0
    NAME = ""
    DESCRIPTION = ""
    MANA_COST = 0
    ORIGINAL_COUNT = DEFAULT_SPELL_ORIGINAL_COUNT
    ERROR_MESSAGE = "Invalid spell invocation"

    def to_dto(self, count: int):
        return SpellDto(
            id=self.ID,
            name=self.NAME,
            description=self.DESCRIPTION,
            manaCost=self.MANA_COST,
            count=count,
            maxCount=self.ORIGINAL_COUNT,
        )

    def to_partial_dto(self):
        return PartialSpellDto(
            id=self.ID,
            name=self.NAME,
            description=self.DESCRIPTION,
            manaCost=self.MANA_COST,
        )

    @classmethod
    def to_partial_dto(cls):
        return PartialSpellDto(
            id=cls.ID,
            name=cls.NAME,
            description=cls.DESCRIPTION,
            manaCost=cls.MANA_COST,
        )

    def get_possible_targets(
        self, board: "GameBoard", from_player1: bool
    ) -> list[Coordinates]:
        raise NotImplementedError

    def invoke(
        self, coordinates: Coordinates, board: "GameBoard", invocator: CellOwner
    ):
        raise NotImplementedError

    def get_metadata_dto(self) -> None | Any:
        return None
