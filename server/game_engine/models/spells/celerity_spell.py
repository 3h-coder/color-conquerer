from typing import TYPE_CHECKING

from game_engine.models.cell.cell_owner import CellOwner
from game_engine.models.cell.cell_state import CellState
from game_engine.models.coordinates import Coordinates
from game_engine.models.spells.abstract.positioning_spell import PositioningSpell
from game_engine.models.spells.spell_id import SpellId

if TYPE_CHECKING:
    from game_engine.models.game_board import GameBoard


class CeleritySpell(PositioningSpell):
    ID = SpellId.CELERITY
    NAME = "Celerity"
    DESCRIPTION = "Select a diagonal line of cells to allow them to move and attack twice this turn"
    MANA_COST = 1
    CONDITION_NOT_MET_ERROR_MESSAGE = (
        "You do not have any diagonal line of cells to apply celerity"
    )
    INVALID_SELECTION_ERROR_MESSAGE = (
        "You must select a diagonal line of friendly cells to apply celerity"
    )

    def get_possible_targets(self, transient_board: "GameBoard", from_player1: bool):
        possible_targets: list[Coordinates] = []
        cell_coordinates = self._initialize_target_searching(
            transient_board, from_player1
        )

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
        for diagonal_index, diagonal in enumerate(all_diagonals):
            self._update_transient_board(transient_board, diagonal)
            # Make sure each cell is bound to only one diagonal
            for cell_coords in diagonal:
                if cell_coords not in self._formation_per_cell:
                    self._formation_per_cell[cell_coords] = diagonal_index
                    self._already_associated_cells.add(cell_coords)

            self._cell_formations.append(diagonal)
            possible_targets.extend(diagonal)

        return possible_targets

    def invoke(
        self, coordinates: Coordinates, board: "GameBoard", invocator: CellOwner
    ):
        diagonal_index = self._formation_per_cell[coordinates]
        diagonal = self._cell_formations[diagonal_index]

        for cell_coords in diagonal:
            cell = board.get(cell_coords.row_index, cell_coords.column_index)
            cell.add_modifier(CellState.ACCELERATED)

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

    # endregion
