from dto.coordinates_dto import CoordinatesDto
from dto.server_only.match_action_dto import ActionType
from game_engine.models.actions.cell_action import CellAction
from game_engine.models.cell.cell import Cell
from utils.board_utils import get_neighbours


class CellAttack(CellAction):
    """
    Represents a cell attacking another.
    """

    def __eq__(self, other):
        return (
            isinstance(other, CellAttack)
            and other.cell_id == self.cell_id
            and other.impacted_coords == self.impacted_coords
            and other.originating_coords == self.originating_coords
        )

    def to_dto(self):
        match_action_dto = super().to_dto()
        match_action_dto.type = ActionType.CELL_ATTACK
        return match_action_dto

    @staticmethod
    def create(
        from_player1: bool,
        cell_id: str,
        row_index: int,
        column_index: int,
        attack_row_index: int,
        attack_column_index: int,
    ):
        return CellAttack(
            from_player1=from_player1,
            is_direct=True,
            impacted_coords=CoordinatesDto(attack_row_index, attack_column_index),
            originating_coords=CoordinatesDto(row_index, column_index),
            cell_id=cell_id,
        )

    @staticmethod
    def calculate(
        cell: Cell,
        from_player1: bool,
        board_array: list[list[Cell]],
        transient_board_array: list[list[Cell]],
    ):
        """
        Returns a set of attacks that an owned cell can perform.
        """
        row_index, column_index = cell.row_index, cell.column_index

        attacks: set[CellAttack] = set()
        neighbours: list[Cell] = get_neighbours(
            cell.row_index, cell.column_index, board_array
        )
        for neighbour in neighbours:
            if not cell.is_hostile_to(neighbour):
                continue

            transient_board_cell = transient_board_array[neighbour.row_index][
                neighbour.column_index
            ]
            transient_board_cell.set_can_be_attacked()

            attacks.add(
                CellAttack.create(
                    from_player1,
                    cell.id,
                    row_index,
                    column_index,
                    neighbour.row_index,
                    neighbour.column_index,
                )
            )
        return attacks
