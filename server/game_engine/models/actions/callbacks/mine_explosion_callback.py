from typing import TYPE_CHECKING

from dto.actions.action_callback_dto import ActionCallbackDto
from game_engine.models.actions.abstract.action_callback import ActionCallback
from game_engine.models.actions.callbacks.action_callback_id import ActionCallBackId
from game_engine.models.dtos.coordinates import Coordinates
from game_engine.models.game_board import GameBoard
from game_engine.models.spells.mine_trap_spell import MineTrapSpell

if TYPE_CHECKING:
    from game_engine.models.actions.abstract.action import Action


class MineExplosionCallback(ActionCallback):
    """
    Deals damage to all cells around the land mine cell.
    """

    ID = ActionCallBackId.MINE_EXPLOSION
    SPELL_CAUSE = MineTrapSpell
    # A mine explosion will trigger surrounding mines
    CALLBACKS = {ActionCallBackId.MINE_EXPLOSION}

    def __init__(self, parent_action: "Action", parent_callback: ActionCallback = None):
        super().__init__(parent_action, parent_callback)
        self.explosion_center_coords: Coordinates | None = None

    def __eq__(self, other):
        return (
            isinstance(other, MineExplosionCallback)
            and self.ID == other.ID
            and self.parent_action == other.parent_action
            and self.parent_callback == other.parent_callback
            and self.explosion_center_coords == other.explosion_center_coords
        )

    def __hash__(self):
        return hash(
            (
                self.ID,
                self.parent_action,
                self.parent_callback,
                self.explosion_center_coords,
            )
        )

    def to_dto(self, for_player1: bool):
        dto: ActionCallbackDto = super().to_dto(for_player1)
        dto.impactedCoords = self.explosion_center_coords.to_dto()
        return dto

    def can_be_triggered(self, match_context):
        if self.explosion_center_coords is not None:
            return True

        parent_action = self.parent_action

        self.explosion_center_coords = impacted_coords = (
            parent_action.metadata.impacted_coords
        )
        impacted_cell = match_context.game_board.get(
            impacted_coords.row_index, impacted_coords.column_index
        )
        return impacted_cell.is_mine_trap()

    def register_callbacks(self, match_context):
        game_board = match_context.game_board
        row_index, col_index = (
            self.explosion_center_coords.row_index,
            self.explosion_center_coords.column_index,
        )

        processed_mines = set()
        explosions_per_radius = {}
        self._scan_for_neighbour_mines(
            game_board,
            (row_index, col_index),
            (row_index, col_index),
            processed_mines,
            explosions_per_radius,
        )
        # add the explosion callbacks from the closest ones to the farthest ones
        for radius in explosions_per_radius:
            self._callbacks_to_trigger += explosions_per_radius[radius]

    @ActionCallback.check_for_callbacks
    @ActionCallback.update_game_board_and_player_resources
    def trigger(self, match_context):
        game_board = match_context.game_board

        row_index, column_index = (
            self.explosion_center_coords.row_index,
            self.explosion_center_coords.column_index,
        )
        impacted_cell = game_board.get(row_index, column_index)

        neighbour_cells = match_context.game_board.get_neighbours(
            row_index, column_index
        )
        player1_resources, player2_resources = (
            match_context.get_both_players_resources()
        )

        death_list = self.deaths
        # Damage all neighbour cells
        for cell in neighbour_cells:
            cell.damage(player1_resources, player2_resources, death_list=death_list)

        # Damage the cell itself
        impacted_cell.damage(
            player1_resources, player2_resources, death_list=death_list
        )

        # The cell is not longer a mine trap
        impacted_cell.hidden_state_info.reset()

    def _scan_for_neighbour_mines(
        self,
        game_board: GameBoard,
        coords: tuple[int, int],
        origin_coords: tuple[int, int],
        processed_mines: set,
        explosions_per_radius: dict[int, list["MineExplosionCallback"]],
    ):
        """
        Will recursively scan the neighbour mines to add chained explosions
        into the given dictionary.
        """
        current_mine_coords = coords
        if current_mine_coords in processed_mines:
            return

        processed_mines.add(current_mine_coords)

        row_index, col_index = coords
        origin_row, origin_col = origin_coords

        # Calculate Manhattan distance from origin explosion
        current_radius = abs(row_index - origin_row) + abs(col_index - origin_col)
        if current_radius > 0:  # Don't add the origin mine
            if current_radius not in explosions_per_radius:
                explosions_per_radius[current_radius] = []

            callback = MineExplosionCallback(self.parent_action, self)
            callback.explosion_center_coords = game_board.get(
                row_index, col_index
            ).get_coordinates()
            callback.can_trigger_callbacks = False
            explosions_per_radius[current_radius].append(callback)

        neighbours = game_board.get_neighbours(row_index, col_index)
        mine_neighbours = [
            neighbour for neighbour in neighbours if neighbour.is_mine_trap()
        ]

        for neighbour in mine_neighbours:
            self._scan_for_neighbour_mines(
                game_board,
                (neighbour.row_index, neighbour.column_index),
                (origin_row, origin_col),
                processed_mines,
                explosions_per_radius,
            )
