from typing import TYPE_CHECKING

from config.logging import get_configured_logger
from constants.game_constants import SPELLS_MANA_COST
from game_engine.models.cell.cell_owner import CellOwner
from game_engine.models.cell.cell_state import CellState
from game_engine.models.dtos.coordinates import Coordinates
from game_engine.models.spells.abstract.spell import Spell
from game_engine.models.spells.spell_id import SpellId

if TYPE_CHECKING:
    from game_engine.models.game_board import GameBoard


class ArcheryVowSpell(Spell):
    ID = SpellId.ARCHERY_VOW
    NAME = "Archery Vow"
    DESCRIPTION = "Select a minion cell with no neighbours to grant them the ability to attack from a distance."
    MANA_COST = SPELLS_MANA_COST.get(ID, 0)
    CONDITION_NOT_MET_ERROR_MESSAGE = (
        "You do not have any minion cell with no neighbours to apply archery vow"
    )
    INVALID_SELECTION_ERROR_MESSAGE = (
        "You must select a minion cell with no neighbours to apply archery vow"
    )

    def get_possible_targets(self, transient_board: "GameBoard", from_player1: bool):
        possible_targets: list[Coordinates] = []
        cell_pool = transient_board.get_cells_owned_by_player(from_player1)

        for cell in cell_pool:
            if (
                cell.is_master
                or len(ArcheryVowSpell._get_owned_neighbours(cell, transient_board)) > 0
            ):
                continue

            cell.set_can_be_spell_targetted()
            possible_targets.append(cell.get_coordinates())

        return possible_targets

    def invoke(
        self, coordinates: Coordinates, board: "GameBoard", invocator: CellOwner
    ):
        cell = board.get(coordinates.row_index, coordinates.column_index)
        cell.add_modifier(CellState.ARCHER)

    @staticmethod
    def _get_owned_neighbours(cell: Coordinates, board: "GameBoard"):
        return board.get_owned_neighbours(cell.row_index, cell.column_index)
