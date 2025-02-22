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

        attacking_is_master = attacking_cell.is_master
        target_is_master = target_cell.is_master

        player1_game_info = match_context.get_player_resources(player1=True)
        player2_game_info = match_context.get_player_resources(player1=False)

        attacker_game_info = (
            player1_game_info
            if attacking_cell.belongs_to_player_1()
            else player2_game_info
        )
        target_game_info = (
            player1_game_info
            if attacker_game_info == player2_game_info
            else player2_game_info
        )
        # endregion

        # 2 master cells clash
        if attacking_is_master and target_is_master:
            attacker_game_info.current_hp -= 1
            target_game_info.current_hp -= 1

        # master attack
        elif attacking_is_master:
            attacker_game_info.current_hp -= 1
            target_cell.set_idle()  # target cell is destroyed

        # attack on master
        elif target_is_master:
            target_game_info.current_hp -= 1
            attacking_cell.set_idle()  # attacking cell is destroyed

        # regular cell clash
        else:
            attacking_cell.set_idle()
            target_cell.set_idle()

        # The following code is technically not necessary as the game should end if a player's HP reaches 0,
        # but it's a good practice to keep the board consistent.
        if attacker_game_info.current_hp <= 0:
            attacking_cell.set_idle()
        if target_game_info.current_hp <= 0:
            target_cell.set_idle()
