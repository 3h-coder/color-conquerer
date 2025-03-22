from typing import TYPE_CHECKING

from dto.misc.coordinates_dto import CoordinatesDto
from dto.spell.metadata.shield_formation_metadata_dto import ShieldFormationMetadataDto
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
        # Each cell is bound to a specific square.
        # A cell can overlap on multiple squares, so we will have to choose which square
        # it is associated with.

        # The cooordinates key represent the cell, the int value represents the square index in _cell_squares list
        self._cell_per_square: dict[Coordinates, int] = {}
        self._cell_squares: list[list[Coordinates]] = []

    def get_possible_targets(self, transient_board: "GameBoard", from_player1: bool):
        possible_targets: list[Coordinates] = []
        cell_pool = transient_board.get_cells_owned_by_player(from_player1)

        # Convert cell pool to a set of coordinates for faster lookup
        cell_coordinates = {(cell.row_index, cell.column_index) for cell in cell_pool}

        # For each cell, try to form squares treating it as the top-left corner
        for top_left_cell in cell_pool:
            row = top_left_cell.row_index
            col = top_left_cell.column_index

            largest_valid_square = self._find_largest_valid_square(
                cell_coordinates, row, col
            )

            if largest_valid_square is not None:
                self._update_transient_board(transient_board, largest_valid_square)
                self._cell_squares.append(largest_valid_square)
                possible_targets.extend(largest_valid_square)

        return possible_targets

    def invoke(
        self, coordinates: Coordinates, board: "GameBoard", invocator: CellOwner
    ):
        corresponding_square_index = self._cell_per_square[coordinates]
        corresponding_square = self._cell_squares[corresponding_square_index]

        for cell_coords in corresponding_square:
            cell = board.get(cell_coords.row_index, cell_coords.column_index)
            cell.state.add_modifier(CellState.SHIELDED)

    def get_metadata_dto(self):
        square_per_coordinates: dict[str, int] = {}
        squares_dto: list[list[CoordinatesDto]] = []

        for square_index, square in enumerate(self._cell_squares):
            square_dto = [coords.to_dto() for coords in square]
            squares_dto.append(square_dto)

            for coords in square:
                coord_key = f"{coords.row_index},{coords.column_index}"
                square_per_coordinates[coord_key] = square_index

        return ShieldFormationMetadataDto(
            squarePerCoordinates=square_per_coordinates, squares=squares_dto
        )

    # region Private methods

    def _find_largest_valid_square(
        self, cell_coordinates: Coordinates, row: int, col: int
    ):
        size = 1
        largest_valid_square: list[Coordinates] = None
        while True:
            # Check if the bottom-right cell exists and belongs to the player
            bottom_right = (row + size, col + size)
            if bottom_right not in cell_coordinates:
                break

                # Check if all cells in the square belong to the player
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
                largest_valid_square = coordinates_square
            else:
                break

            size += 1

        return largest_valid_square

    def _update_transient_board(
        self, transient_board: "GameBoard", largest_valid_square: list[Coordinates]
    ):
        for coords in largest_valid_square:
            transient_cell = transient_board.get(coords.row_index, coords.column_index)
            transient_cell.transient_state = CellTransientState.CAN_BE_SPELL_TARGETTED

    # endregion
