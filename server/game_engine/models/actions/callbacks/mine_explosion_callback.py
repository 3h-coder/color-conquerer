from typing import TYPE_CHECKING

from dto.coordinates_dto import CoordinatesDto
from game_engine.models.actions.callbacks.action_callback import ActionCallback
from game_engine.models.actions.callbacks.action_callback_id import ActionCallBackId

if TYPE_CHECKING:
    from game_engine.models.actions.action import Action


class MineExplosionCallback(ActionCallback):
    """
    Deals damage to all cells around the land mine cell.
    """

    ID = ActionCallBackId.MINE_EXPLOSION

    def __init__(self, parent_action: "Action"):
        super().__init__(parent_action)
        self.explosion_center_coords: CoordinatesDto | None = None

    def can_be_triggered(self, match_context):
        parent_action = self.parent_action

        self.explosion_center_coords = impacted_coords = parent_action.impacted_coords
        impacted_cell = match_context.game_board.get(
            impacted_coords.rowIndex, impacted_coords.columnIndex
        )
        return impacted_cell.is_mine_trap()

    @ActionCallback.update_game_board_and_player_resources
    def trigger(self, match_context):
        game_board = match_context.game_board

        row_index, column_index = (
            self.explosion_center_coords.rowIndex,
            self.explosion_center_coords.columnIndex,
        )
        impacted_cell = game_board.get(row_index, column_index)

        neighbour_cells = match_context.game_board.get_neighbours(
            row_index, column_index
        )
        player1_resources, player2_resources = match_context.get_both_player_resources()

        # Damage all neighbour cells
        for cell in neighbour_cells:
            cell.damage(player1_resources, player2_resources)

        # Damage the cell itself
        impacted_cell.damage(player1_resources, player2_resources)

        # The cell is not longer a mine trap
        impacted_cell.hidden_state_info.reset()
