from typing import TYPE_CHECKING

from game_engine.models.cell.cell_owner import CellOwner
from game_engine.models.cell.cell_state import CellState
from game_engine.models.cell.cell_transient_state import CellTransientState
from game_engine.models.coordinates import Coordinates
from game_engine.models.spells.spell import Spell
from game_engine.models.spells.spell_id import SpellId

if TYPE_CHECKING:
    from game_engine.models.game_board import GameBoard


class ShieldFormationSpell(Spell):
    ID = SpellId.SHIELD_FORMATION
    NAME = "Shield formation"
    DESCRIPTION = "Select a square cell formation to apply a shield to each."
    MANA_COST = 3

    def __init__(self):
        super().__init__()
        # Each cell is bound to a specific square
        self._squares_of_cells: list[list[Coordinates]] = []

    def get_possible_targets(self, transient_board: "GameBoard", from_player1: bool):
        possible_targets: list[Coordinates] = []
        cell_pool = transient_board.get_cells_owned_by_player(from_player1)

        # Convert cell pool to a set of coordinates for faster lookup
        cell_coordinates = {(cell.row_index, cell.column_index) for cell in cell_pool}

        # For each cell, try to form squares treating it as top-left corner
        for top_left_cell in cell_pool:
            row = top_left_cell.row_index
            col = top_left_cell.column_index

            size = 1
            while True:
                # Check if bottom-right cell exists and belongs to player
                bottom_right = (row + size, col + size)
                if bottom_right not in cell_coordinates:
                    break

                # Check if all cells in the square belong to player
                valid_square = True
                coordinates_square: list[Coordinates] = []
                for r in range(row, row + size + 1):
                    for c in range(col, col + size + 1):
                        if (r, c) not in cell_coordinates:
                            valid_square = False
                            break
                        coordinates_square.append(Coordinates(r, c))
                    if not valid_square:
                        break

                if valid_square:
                    # Only set the transient state if the square is valid
                    for coords in coordinates_square:
                        transient_cell = transient_board.get(
                            coords.row_index, coords.column_index
                        )
                        transient_cell.transient_state = (
                            CellTransientState.CAN_BE_SPELL_TARGETTED
                        )
                    self._squares_of_cells.append(coordinates_square)
                    possible_targets.extend(coordinates_square)

                size += 1

        return possible_targets

    def invoke(
        self, coordinates: Coordinates, board: "GameBoard", invocator: CellOwner
    ):
        corresponding_square: list[Coordinates] = []
        for square in self._squares_of_cells:
            if coordinates in square:
                corresponding_square = square
                break

        for cell_coords in corresponding_square:
            cell = board.get(cell_coords.row_index, cell_coords.column_index)
            cell.state.add_modifier(CellState.SHIELDED)
