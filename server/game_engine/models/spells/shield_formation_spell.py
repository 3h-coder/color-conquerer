from typing import TYPE_CHECKING

from dto.misc.coordinates_dto import CoordinatesDto
from dto.spell.metadata.shield_formation_metadata_dto import ShieldFormationMetadataDto
from game_engine.models.cell.cell_owner import CellOwner
from game_engine.models.cell.cell_state import CellState
from game_engine.models.cell.cell_transient_state import CellTransientState
from game_engine.models.coordinates import Coordinates
from game_engine.models.spells.abstract.positioning_spell import PositioningSpell
from game_engine.models.spells.spell_id import SpellId

if TYPE_CHECKING:
    from game_engine.models.game_board import GameBoard


class ShieldFormationSpell(PositioningSpell):
    ID = SpellId.SHIELD_FORMATION
    NAME = "Shield formation"
    DESCRIPTION = "Select a square cell formation to apply a shield to each."
    MANA_COST = 3
    CONDITION_NOT_MET_ERROR_MESSAGE = "You do not have any square of cells to shield"

    def __init__(self):
        super().__init__()
        # Each cell is bound to a specific square.
        # A cell can overlap on multiple squares, so we will have to choose which square
        # it is associated with.
        # The cooordinates key represent the cell, the int value represents the square index in _cell_squares list
        self._square_per_cell: dict[Coordinates, int] = {}
        self._cell_squares: list[list[Coordinates]] = []

    def get_possible_targets(self, transient_board: "GameBoard", from_player1: bool):
        possible_targets: list[Coordinates] = []
        cell_coordinates = self._initialize_target_searching(
            transient_board, from_player1
        )

        # For each cell, try to form squares treating it as the top-left corner
        for top_left_cell_coords in cell_coordinates:
            row, col = top_left_cell_coords

            if (row, col) in self._already_associated_cells:
                continue

            largest_valid_square = self._find_largest_valid_square(
                cell_coordinates, row, col
            )

            if largest_valid_square is not None:
                self._update_transient_board(transient_board, largest_valid_square)
                self._cell_squares.append(largest_valid_square)
                possible_targets.extend(largest_valid_square)

                for cell in largest_valid_square:
                    if cell in self._already_associated_cells:
                        continue

                    self._already_associated_cells.add(cell)
                    self._square_per_cell[cell] = len(self._cell_squares) - 1

        return possible_targets

    def invoke(
        self, coordinates: Coordinates, board: "GameBoard", invocator: CellOwner
    ):
        corresponding_square_index = self._square_per_cell[coordinates]
        corresponding_square = self._cell_squares[corresponding_square_index]

        for cell_coords in corresponding_square:
            cell = board.get(cell_coords.row_index, cell_coords.column_index)
            cell.add_modifier(CellState.SHIELDED)

    def get_metadata_dto(self):
        squares_dto: list[list[CoordinatesDto]] = []

        squares_dto = [
            [coords.to_dto() for coords in square] for square in self._cell_squares
        ]

        # ⚠️ The key format "row_index,col_index" is being used by the client
        square_per_coordinates = {
            f"{cell.row_index},{cell.column_index}": square_index
            for (cell, square_index) in self._square_per_cell.items()
        }

        return ShieldFormationMetadataDto(
            squarePerCoordinates=square_per_coordinates, squares=squares_dto
        )

    # region Private methods

    def _find_largest_valid_square(
        self, cell_coordinates: Coordinates, row: int, col: int
    ) -> None | list[Coordinates]:
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

    # endregion
