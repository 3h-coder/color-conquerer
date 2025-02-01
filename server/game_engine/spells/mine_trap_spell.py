from dto.coordinates_dto import CoordinatesDto
from game_engine.spells.spell import Spell
from game_engine.spells.spell_id import Spell_ID

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game_engine.models.cell import Cell


class MineTrapSpell(Spell):
    ID = Spell_ID.MINE_TRAP
    NAME = "Mine Trap"
    DESCRIPTION = (
        "Places a mine trap on a non-occupied cell. "
        "When an enemy cell steps or spawns on it, it explodes, "
        "dealing 1 damage to all adjacent cells."
    )
    MANA_COST = 2

    def __init__(self):
        super().__init__(
            id=self.ID,
            name=self.NAME,
            description=self.DESCRIPTION,
            mana_cost=self.MANA_COST,
        )

    def get_possible_targets(self, board: list[list["Cell"]]):
        possible_targets = []

        for row in board:
            for cell in row:
                if cell.is_owned():
                    continue

                cell.set_can_be_spell_targetted()
                possible_targets.append(cell)

        return possible_targets

    def invoke(self, coordinates: CoordinatesDto, board: list[list["Cell"]]):
        cell = board[coordinates.rowIndex][coordinates.columnIndex]
        cell.set_as_mine_trap()
        return board
