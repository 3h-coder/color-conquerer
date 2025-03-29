from typing import TYPE_CHECKING

from config.logging import get_configured_logger
from dto.misc.coordinates_dto import CoordinatesDto
from dto.spell.metadata.celerity_metadata_dto import CelerityMetadataDto
from game_engine.models.cell.cell_owner import CellOwner
from game_engine.models.cell.cell_transient_state import CellTransientState
from game_engine.models.coordinates import Coordinates
from game_engine.models.spells.spell import Spell
from game_engine.models.spells.spell_id import SpellId

if TYPE_CHECKING:
    from game_engine.models.game_board import GameBoard


class CeleritySpell(Spell):
    ID = SpellId.CELERITY
    NAME = "Celerity"
    DESCRIPTION = "Select a diagonal line of cells to allow them to move and attack twice this turn"
    MANA_COST = 0
    CONDITION_NOT_MET_ERROR_MESSAGE = (
        "You do not have any diagonal line of cells to apply celerity"
    )

    def __init__(self):
        super().__init__()
        self._logger = get_configured_logger(__name__)
        self._diagonal_per_cell: dict[Coordinates, int] = {}
        self._cell_diagonals: list[list[Coordinates]] = []
        self._already_associated_cells: set[Coordinates] = set()

    def get_possible_targets(self, transient_board: "GameBoard", from_player1: bool):
        if len(self._already_associated_cells) > 0:
            self._already_associated_cells = set()

        possible_targets: list[Coordinates] = []
        cell_pool = transient_board.get_cells_owned_by_player(from_player1)

        # Convert cell pool to a set of coordinates for faster lookup
        cell_coordinates = {(cell.row_index, cell.column_index) for cell in cell_pool}
        diagonals1 = []
        diagonals2 = []

        for cell_coords in cell_coordinates:
            if cell_coords in self._already_associated_cells:
                continue

            row, col = cell_coords

            diagonal1, diagonal2 = self._get_diagonals(cell_coordinates, row, col)

            self._add_diagonal(diagonals1, diagonal1)
            self._add_diagonal(diagonals2, diagonal2)

        all_diagonals = diagonals1 + diagonals2
        self._logger.debug(f"Found {len(all_diagonals)} diagonals: {all_diagonals}")
        for diagonal_index, diagonal in enumerate(all_diagonals):
            self._update_transient_board(transient_board, diagonal)
            # Make sure each cell is bound to only one diagonal
            for cell_coords in diagonal:
                if cell_coords not in self._diagonal_per_cell:
                    self._diagonal_per_cell[cell_coords] = diagonal_index
                    self._already_associated_cells.add(cell_coords)

            self._cell_diagonals.append(diagonal)
            possible_targets.extend(diagonal)

        return possible_targets

    def invoke(
        self, coordinates: Coordinates, board: "GameBoard", invocator: CellOwner
    ):
        diagonal_index = self._diagonal_per_cell[coordinates]
        diagonal = self._cell_diagonals[diagonal_index]

        for cell_coords in diagonal:
            cell = board.get(cell_coords.row_index, cell_coords.column_index)
            # cell.add_celerity_state()

    def get_metadata_dto(self):
        diagonals_dto: list[list[CoordinatesDto]] = []
        diagonals_dto = [
            [coords.to_dto() for coords in diagonal]
            for diagonal in self._cell_diagonals
        ]
        # ⚠️ The key format "row_index,col_index" is being used by the client
        diagonal_per_coordinates = {
            f"{coords.row_index},{coords.column_index}": self._diagonal_per_cell[coords]
            for coords in self._diagonal_per_cell
        }

        return CelerityMetadataDto(
            diagonalPerCoordinates=diagonal_per_coordinates,
            diagonals=diagonals_dto,
        )

    # region Private methods

    def _get_diagonals(
        self, cell_coordinates: set[tuple[int, int]], row: int, col: int
    ) -> tuple[list[Coordinates], list[Coordinates]]:
        # Diagonal from top-left to bottom-right
        diagonal1 = []
        r, c = row, col
        while (r, c) in cell_coordinates:
            diagonal1.append(Coordinates(r, c))
            r += 1
            c += 1

        # Diagonal from bottom-left to top-right
        diagonal2 = []
        r, c = row, col
        while (r, c) in cell_coordinates:
            diagonal2.append(Coordinates(r, c))
            r -= 1
            c += 1

        diagonal1 = diagonal1 if len(diagonal1) > 1 else []
        diagonal2 = diagonal2 if len(diagonal2) > 1 else []

        return diagonal1, diagonal2

    def _add_diagonal(
        self, diagonals: list[list[Coordinates]], diagonal: list[Coordinates]
    ):
        """
        Add a diagonal to the list of diagonals, ensuring that no two diagonals are subsets of each other.
        """
        if not diagonal:
            return

        diagonals[:] = [
            diag for diag in diagonals if not set(diag).issubset(set(diagonal))
        ]
        diagonals.append(diagonal)

    def _update_transient_board(
        self, transient_board: "GameBoard", diagonal: list[Coordinates]
    ):
        for coords in diagonal:
            transient_cell = transient_board.get(coords.row_index, coords.column_index)
            transient_cell.transient_state = CellTransientState.CAN_BE_SPELL_TARGETTED

    # endregion
