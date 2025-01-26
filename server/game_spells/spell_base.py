from dto.coordinates_dto import CoordinatesDto
from game_spells.spell_id import Spell_ID

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dto.server_only.cell_info_dto import CellInfoDto


class SpellBase:
    """
    Base class for all spells.
    """

    def __init__(self, id: Spell_ID, description: str, mana_cost: int):
        self.id = id
        self.description = description
        self.mana_cost = mana_cost

    def get_possible_targets(self, board: list[list["CellInfoDto"]]):
        raise NotImplementedError

    def invoke(self, coordinates: CoordinatesDto, board: list[list["CellInfoDto"]]):
        raise NotImplementedError
