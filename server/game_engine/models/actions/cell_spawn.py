from dataclasses import dataclass

from dto.coordinates_dto import CoordinatesDto
from dto.match_action_dto import ActionType, MatchActionDto
from game_engine.models.actions.action import Action
from game_engine.models.cell.cell import Cell
from game_engine.models.game_board import GameBoard
from game_engine.models.match_context import MatchContext


@dataclass
class CellSpawn(Action):
    """
    Represents a friendly/enemy cell being summoned.
    """

    DEFAULT_MANA_COST = 1

    def __init__(self, from_player1: bool, impacted_coords: CoordinatesDto):
        super().__init__(
            from_player1=from_player1,
            impacted_coords=impacted_coords,
        )

    def __eq__(self, other):
        return (
            isinstance(other, CellSpawn)
            and other.impacted_coords == self.impacted_coords
        )

    def __hash__(self):
        return hash(self.impacted_coords)

    def to_dto(self):
        return MatchActionDto(
            player1=self.from_player1,
            type=ActionType.CELL_SPAWN,
            originatingCellCoords=None,
            impactedCoords=self.impacted_coords,
            spell=None,
        )

    @staticmethod
    def create(from_player1: bool, row_index: int, column_index: int):
        return CellSpawn(
            from_player1=from_player1,
            impacted_coords=CoordinatesDto(row_index, column_index),
        )

    @staticmethod
    def calculate(
        from_player1: bool,
        transient_game_board: GameBoard,
    ):
        """
        Returns a set of spawns that a player can perform.
        """
        possible_spawns: set[CellSpawn] = set()

        owned_cells = transient_game_board.get_cells_owned_by_player(from_player1)
        for cell in owned_cells:
            row_index, column_index = cell.row_index, cell.column_index
            neighbours: list[Cell] = transient_game_board.get_neighbours(
                row_index, column_index
            )
            for neighbour in neighbours:
                if neighbour.is_owned():
                    continue

                transient_board_cell = transient_game_board.get(
                    neighbour.row_index, neighbour.column_index
                )
                transient_board_cell.set_can_be_spawned_into()

                possible_spawns.add(
                    CellSpawn.create(
                        from_player1, neighbour.row_index, neighbour.column_index
                    )
                )

        return possible_spawns

    def apply(self, match_context: MatchContext):
        """
        Spawns a cell at the given coordinates for the given player.
        """
        target_coords = self.impacted_coords
        cell = match_context.game_board.get(
            target_coords.rowIndex, target_coords.columnIndex
        )
        if self.from_player1:
            cell.set_owned_by_player1()
            cell.set_freshly_spawned()
        else:
            cell.set_owned_by_player2()
            cell.set_freshly_spawned()
