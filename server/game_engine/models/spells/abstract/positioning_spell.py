from typing import TYPE_CHECKING

from dto.misc.coordinates_dto import CoordinatesDto
from dto.spell.metadata.positioning_info_dto import PositioningInfoDto
from game_engine.models.cell.cell_transient_state import CellTransientState
from game_engine.models.dtos.coordinates import Coordinates
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
        # A formation represents a specific arrangement of cells.
        # A cell can overlap on multiple formations, so we will have to choose which formation
        # it is associated with.
        # The coordinates key represent the cell, the int value represents the formation index in _cell_formations list
        self._formation_per_cell: dict[Coordinates, int] = {}
        self._cell_formations: list[list[Coordinates]] = []
        self._already_associated_cells: set[Coordinates] = set()

    def get_metadata_dto(self):
        """
        Returns the metadata of the spell, including the cell formation and the mapping
        of coordinates to formation indices.
        """
        formations_dto: list[list[CoordinatesDto]] = []

        formations_dto = [
            [coords.to_dto() for coords in square] for square in self._cell_formations
        ]

        # ⚠️ The key format "row_index,col_index" is being used by the client
        formation_per_coordinates = {
            PositioningSpell.coordinates_to_key_string(cell_coords): square_index
            for (cell_coords, square_index) in self._formation_per_cell.items()
        }

        return PositioningInfoDto(
            formationPerCoordinates=formation_per_coordinates,
            cellFormations=formations_dto,
        )

    @staticmethod
    def coordinates_to_key_string(coordinates: Coordinates):
        """⚠️ The key format "row_index,col_index" is being used by the client"""
        return f"{coordinates.row_index},{coordinates.column_index}"

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
