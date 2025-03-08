from typing import TYPE_CHECKING

from config.logging import get_configured_logger
from dto.action_callback_dto import ActionCallbackDto
from dto.coordinates_dto import CoordinatesDto
from game_engine.models.actions.callbacks.action_callback import ActionCallback
from game_engine.models.actions.callbacks.action_callback_id import ActionCallBackId
from game_engine.models.spells.mine_trap_spell import MineTrapSpell

if TYPE_CHECKING:
    from game_engine.models.actions.action import Action

_logger = get_configured_logger(__name__)


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
        self.explosion_center_coords: CoordinatesDto | None = None

    def to_dto(self, for_player1: bool):
        dto: ActionCallbackDto = super().to_dto(for_player1)
        dto.impactedCoords = self.explosion_center_coords
        return dto

    def can_be_triggered(self, match_context):
        if self.explosion_center_coords is not None:
            return True

        parent_action = self.parent_action

        self.explosion_center_coords = impacted_coords = parent_action.impacted_coords
        impacted_cell = match_context.game_board.get(
            impacted_coords.rowIndex, impacted_coords.columnIndex
        )
        return impacted_cell.is_mine_trap()

    def register_callbacks(self, match_context):
        game_board = match_context.game_board
        neighbours = game_board.get_neighbours(
            self.explosion_center_coords.rowIndex,
            self.explosion_center_coords.columnIndex,
        )

        for neighbour in neighbours:
            if neighbour.is_mine_trap():
                callback = MineExplosionCallback(self.parent_action, self)
                callback.explosion_center_coords = neighbour.get_coordinates()
                self._callbacks_to_trigger.add(callback)

    @ActionCallback.check_for_callbacks
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
