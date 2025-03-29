from typing import TYPE_CHECKING

from game_engine.models.cell.cell_transient_state import CellTransientState
from game_engine.models.coordinates import Coordinates
from game_engine.models.spells.abstract.spell import Spell

if TYPE_CHECKING:
    from game_engine.models.game_board import GameBoard


class PositioningSpell(Spell):
    """
    Spell that can only be casted on a group of cells placed in a certain way
    (e.g. a line, a square, etc.).
    """

    def __init__(self):
        super().__init__()
        self._already_associated_cells: set[Coordinates] = set()

    def _initialize_target_searching(
        self, transient_board: "GameBoard", from_player1: bool
    ):
        self._already_associated_cells = set()

        cell_pool = transient_board.get_cells_owned_by_player(from_player1)

        # Convert cell pool to a set of coordinates for faster lookup
        cell_coordinates = {(cell.row_index, cell.column_index) for cell in cell_pool}
        return cell_coordinates

    def _update_transient_board(
        self, transient_board: "GameBoard", formation: list[Coordinates]
    ):
        for coords in formation:
            transient_cell = transient_board.get(coords.row_index, coords.column_index)
            transient_cell.transient_state = CellTransientState.CAN_BE_SPELL_TARGETTED
