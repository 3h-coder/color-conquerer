from dto.coordinates_dto import CoordinatesDto
from dto.match_action_dto import ActionType
from game_engine.models.actions.action import Action
from game_engine.models.actions.cell_action import CellAction
from game_engine.models.cell.cell import Cell
from game_engine.models.game_board import GameBoard
from game_engine.models.match_context import MatchContext


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

    def __hash__(self):
        return hash((self.cell_id, self.impacted_coords, self.originating_coords))

    def __repr__(self):
        return (
            f"<CellAttack(from_player1={self.from_player1}, "
            f"impacted_coords={self.impacted_coords}, "
            f"originating_coords={self.originating_coords}, "
            f"cell_id={self.cell_id}, "
            f"mana_cost={self.mana_cost}, "
            f"callbacks_to_trigger={self._callbacks_to_trigger})>"
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
            impacted_coords=CoordinatesDto(attack_row_index, attack_column_index),
            originating_coords=CoordinatesDto(row_index, column_index),
            cell_id=cell_id,
        )

    @staticmethod
    def calculate(
        cell: Cell,
        from_player1: bool,
        transient_game_board: GameBoard,
    ):
        """
        Returns a set of attacks that an owned cell can perform.
        """
        row_index, column_index = cell.row_index, cell.column_index

        attacks: set[CellAttack] = set()
        neighbours: list[Cell] = transient_game_board.get_neighbours(
            cell.row_index,
            cell.column_index,
        )
        for neighbour in neighbours:
            if not cell.is_hostile_to(neighbour):
                continue

            transient_board_cell = transient_game_board.get(
                neighbour.row_index, neighbour.column_index
            )
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

    @Action.trigger_hooks_and_check_callbacks
    def apply(self, match_context: MatchContext):
        """
        Triggers an attack between two cells on the board.
        """
        # region Variable setup
        attacker_coords = self.originating_coords
        target_coords = self.impacted_coords

        attacking_row_index, attacking_col_index = (
            attacker_coords.rowIndex,
            attacker_coords.columnIndex,
        )
        target_row_index, target_col_index = (
            target_coords.rowIndex,
            target_coords.columnIndex,
        )

        board = match_context.game_board
        attacking_cell = board.get(attacking_row_index, attacking_col_index)
        target_cell = board.get(target_row_index, target_col_index)

        # Should never happen, but just in case
        if attacking_cell.owner == target_cell.owner:
            return

        player1_resources, player2_resources = match_context.get_both_player_resources()
        # endregion

        # Cell clash
        attacking_cell.damage(player1_resources, player2_resources)
        target_cell.damage(player1_resources, player2_resources)
