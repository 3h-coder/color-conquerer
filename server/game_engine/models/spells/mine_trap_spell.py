from typing import TYPE_CHECKING

from dto.coordinates_dto import CoordinatesDto
from game_engine.models.cell.cell_owner import CellOwner
from game_engine.models.spells.spell import Spell
from game_engine.models.spells.spell_id import SpellId

if TYPE_CHECKING:
    from game_engine.models.game_board import GameBoard


class MineTrapSpell(Spell):
    ID = SpellId.MINE_TRAP
    NAME = "Mine Trap"
    DESCRIPTION = (
        "Place a mine trap on a non-occupied cell. "
        "When an enemy cell steps or spawns on it, it explodes, "
        "dealing 1 damage to all adjacent cells."
    )
    MANA_COST = 2

    def get_possible_targets(self, transient_board: "GameBoard"):
        possible_targets = []

        for row in transient_board.board:
            for cell in row:
                if cell.is_owned():
                    continue

                cell.set_can_be_spell_targetted()
                possible_targets.append(cell)

        return possible_targets

    def invoke(
        self, coordinates: set[CoordinatesDto], board: "GameBoard", invocator: CellOwner
    ):
        coords = next(
            iter(coordinates)
        )  # There should only be one element in coordinates
        cell = board.get(coords.rowIndex, coords.columnIndex)
        cell.set_as_mine_trap(invocator)
