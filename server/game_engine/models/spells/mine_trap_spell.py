from typing import TYPE_CHECKING

from constants.game_constants import SPELLS_MANA_COST
from game_engine.models.cell.cell_owner import CellOwner
from game_engine.models.dtos.coordinates import Coordinates
from game_engine.models.spells.abstract.spell import Spell
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
    MANA_COST = SPELLS_MANA_COST.get(ID, 0)
    CONDITION_NOT_MET_ERROR_MESSAGE = "No available cell"
    INVALID_SELECTION_ERROR_MESSAGE = (
        "You must select an idle cell to place a mine trap onto"
    )

    def get_possible_targets(self, transient_board: "GameBoard", _):
        possible_targets: list[Coordinates] = []

        for row in transient_board.board:
            for cell in row:
                if cell.is_owned():
                    continue

                cell.set_can_be_spell_targetted()
                possible_targets.append(cell.get_coordinates())

        return possible_targets

    def invoke(
        self, coordinates: Coordinates, board: "GameBoard", invocator: CellOwner
    ):
        cell = board.get(coordinates.row_index, coordinates.column_index)
        cell.set_as_mine_trap(invocator)
