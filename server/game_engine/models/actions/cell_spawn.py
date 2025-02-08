from dataclasses import dataclass

from dto.coordinates_dto import CoordinatesDto
from dto.server_only.match_action_dto import ActionType, MatchActionDto
from game_engine.models.actions.action import Action
from game_engine.models.cell.cell import Cell
from utils.board_utils import get_cells_owned_by_player, get_neighbours


@dataclass
class CellSpawn(Action):
    """
    Represents a friendly/enemy cell being summoned.
    """

    DEFAULT_MANA_COST = 1

    def __eq__(self, other):
        return (
            isinstance(other, CellSpawn)
            and other.impacted_coords == self.impacted_coords
        )

    def to_dto(self):
        return MatchActionDto(
            player1=self.from_player1,
            type=ActionType.CELL_SPAWN,
            originatingCellCoords=None,
            impactedCoords=self.impacted_coords,
            isDirect=self.is_direct,
            manaCost=self.mana_cost,
            cellId=None,
            spellId=None,
        )

    @staticmethod
    def create(from_player1: bool, row_index: int, column_index: int):
        return CellSpawn(
            from_player1=from_player1,
            is_direct=True,
            impacted_coords=CoordinatesDto(row_index, column_index),
        )

    @staticmethod
    def calculate(
        from_player1: bool,
        board_array: list[list[Cell]],
        transient_board_array: list[list[Cell]],
    ):
        """
        Returns a set of spawns that a player can perform.
        """
        possible_spawns: set[Action] = set()

        owned_cells = get_cells_owned_by_player(from_player1, board_array)
        for cell in owned_cells:
            row_index, column_index = cell.row_index, cell.column_index
            neighbours: list[Cell] = get_neighbours(
                row_index, column_index, board_array
            )
            for neighbour in neighbours:
                if neighbour.is_owned():
                    continue

                transient_board_cell = transient_board_array[neighbour.row_index][
                    neighbour.column_index
                ]
                transient_board_cell.set_can_be_spawned_into()

                possible_spawns.add(
                    CellSpawn.create(from_player1, row_index, column_index)
                )

        return possible_spawns
