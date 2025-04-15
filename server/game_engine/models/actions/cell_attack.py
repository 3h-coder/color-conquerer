from dto.actions.match_action_dto import ActionType
from game_engine.models.actions.action import Action
from game_engine.models.actions.cell_action import CellAction
from game_engine.models.cell.cell import Cell
from game_engine.models.dtos.cell_attack_metadata import CellAttackMetadata
from game_engine.models.dtos.coordinates import Coordinates
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
            and other.metadata == self.metadata
        )

    def __hash__(self):
        return hash((self.cell_id, self.metadata))

    def __repr__(self):
        return (
            f"<CellAttack(from_player1={self.from_player1}, "
            f"cell_id={self.cell_id}, "
            f"mana_cost={self.mana_cost}, "
            f"metadata={self.metadata}, "
            f"callbacks_to_trigger={self._callbacks_to_trigger})>"
        )

    def to_dto(self):
        match_action_dto = super().to_dto()

        match_action_dto.type = ActionType.CELL_ATTACK
        if isinstance(self.specific_metadata, CellAttackMetadata):
            match_action_dto.specificMetadata = self.specific_metadata.to_dto()

        return match_action_dto

    @staticmethod
    def create(
        from_player1: bool,
        cell_id: str,
        attacker_coordinates: Coordinates,
        target_coordinates: Coordinates,
    ):
        cell_attack = CellAttack(
            from_player1=from_player1,
            impacted_coords=target_coordinates,
            originating_coords=attacker_coordinates,
            cell_id=cell_id,
        )

        cell_attack.specific_metadata = CellAttackMetadata(
            is_ranged_attack=not attacker_coordinates.is_neighbour(target_coordinates)
        )

        return cell_attack

    @staticmethod
    def calculate(
        cell: Cell,
        from_player1: bool,
        transient_game_board: GameBoard,
    ):
        """
        Returns a set of attacks that an owned cell can perform.
        """

        attacks: set[CellAttack] = set()
        if cell.is_archer():
            CellAttack._calculate_all_attacks(
                cell, from_player1, transient_game_board, attacks
            )
        else:
            CellAttack._calculate_neighbour_attacks(
                cell, from_player1, transient_game_board, attacks
            )
        return attacks

    @Action.trigger_hooks_and_check_callbacks
    def apply(self, match_context: MatchContext):
        """
        Triggers an attack between two cells on the board.
        """
        # region Variable setup
        attacker_coords = self.metadata.originating_coords
        target_coords = self.metadata.impacted_coords
        is_ranged_attack = (
            isinstance(self.specific_metadata, CellAttackMetadata)
            and self.specific_metadata.is_ranged_attack
        )

        attacking_row_index, attacking_col_index = (
            attacker_coords.row_index,
            attacker_coords.column_index,
        )
        target_row_index, target_col_index = (
            target_coords.row_index,
            target_coords.column_index,
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
        death_list = self.metadata.deaths
        # If both cell are archers or not, they can attack each other
        if attacking_cell.is_archer() == target_cell.is_archer():
            attacking_cell.damage(
                player1_resources, player2_resources, death_list=death_list
            )
            target_cell.damage(
                player1_resources, player2_resources, death_list=death_list
            )
        # If only the attacker is an archer and the attack is ranged, only the target cell is damaged
        elif attacking_cell.is_archer() and is_ranged_attack:
            target_cell.damage(
                player1_resources, player2_resources, death_list=death_list
            )

    @staticmethod
    def _calculate_all_attacks(
        cell: Cell,
        from_player1: bool,
        transient_game_board: GameBoard,
        attacks: set["CellAttack"],
    ):
        for row in transient_game_board.board:
            for board_cell in row:
                if not board_cell.is_hostile_to(cell):
                    continue

                CellAttack._register_attack(
                    cell, board_cell, from_player1, transient_game_board, attacks
                )

    @staticmethod
    def _calculate_neighbour_attacks(
        cell: Cell,
        from_player1: bool,
        transient_game_board: GameBoard,
        attacks: set["CellAttack"],
    ):
        neighbours: list[Cell] = transient_game_board.get_neighbours(
            cell.row_index,
            cell.column_index,
        )
        for neighbour in neighbours:
            if not cell.is_hostile_to(neighbour):
                continue

            CellAttack._register_attack(
                cell,
                neighbour,
                from_player1,
                transient_game_board,
                attacks,
            )

    @staticmethod
    def _register_attack(
        attacker_cell: Cell,
        target_cell: Cell,
        from_player1: bool,
        transient_game_board: GameBoard,
        attacks: set["CellAttack"],
    ):
        transient_board_cell = transient_game_board.get(
            target_cell.row_index, target_cell.column_index
        )
        transient_board_cell.set_can_be_attacked()

        attacks.add(
            CellAttack.create(
                from_player1,
                attacker_cell.id,
                attacker_cell.get_coordinates(),
                target_cell.get_coordinates(),
            )
        )
