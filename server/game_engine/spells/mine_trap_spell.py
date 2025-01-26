from typing import TYPE_CHECKING

from dto.coordinates_dto import CoordinatesDto
from game_engine.spells.spell_base import SpellBase
from game_engine.spells.spell_id import Spell_ID

if TYPE_CHECKING:
    from dto.server_only.cell_info_dto import CellInfoDto


class MineTrapSpell(SpellBase):
    NAME = "Mine Trap"
    DESCRIPTION = (
        "Places a mine trap on a non-occupied cell."
        "When an enemy cell steps or spawns on it, it explodes, "
        "dealing 1 damage to all adjacent units."
    )
    MANA_COST = 2

    def __init__(self):
        super().__init__(
            id=Spell_ID.MINE_TRAP,
            name=self.NAME,
            description=self.DESCRIPTION,
            mana_cost=self.MANA_COST,
        )

    def get_possible_targets(self, board: list[list["CellInfoDto"]]):
        return [cell for row in board for cell in row if not cell.is_owned()]

    def invoke(self, coordinates: CoordinatesDto, board: list[list["CellInfoDto"]]):
        cell = board[coordinates.rowIndex][coordinates.columnIndex]
        cell.set_as_mine_trap()
        return board
