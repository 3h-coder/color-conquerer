from typing import TYPE_CHECKING

from config.logging import get_configured_logger
from dto.action_callback_dto import ActionCallbackDto
from dto.coordinates_dto import CoordinatesDto
from game_engine.models.actions.callbacks.action_callback import ActionCallback
from game_engine.models.actions.callbacks.action_callback_id import ActionCallBackId
from game_engine.models.game_board import GameBoard
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
        row_index, col_index = (
            self.explosion_center_coords.rowIndex,
            self.explosion_center_coords.columnIndex,
        )

        processed_mines = set()
        explosions_per_radius = {}
        self.scan_for_neighbour_mines(
            game_board, row_index, col_index, processed_mines, explosions_per_radius
        )
        for radius in explosions_per_radius:
            self._callbacks_to_trigger += explosions_per_radius[radius]

        _logger.debug(
            f"Found a total of {len(self._callbacks_to_trigger)} explosion callbacks"
        )

    def scan_for_neighbour_mines(
        self,
        game_board: GameBoard,
        row_index: int,
        col_index: int,
        processed_mines: set,
        explosions_per_radius: dict[int, list["MineExplosionCallback"]],
    ):
        """
        Will recursively scan the neighbour mines to add chained explosions.
        """
        current_mine_key = (row_index, col_index)
        if current_mine_key in processed_mines:
            return

        processed_mines.add(current_mine_key)
        radius = len(explosions_per_radius.keys()) + 1
        if radius not in explosions_per_radius:
            explosions_per_radius[radius] = []

        neighbours = game_board.get_neighbours(row_index, col_index)
        mine_neighbours = [
            neighbour for neighbour in neighbours if neighbour.is_mine_trap()
        ]

        for neighbour in mine_neighbours:
            callback = MineExplosionCallback(self.parent_action, self)
            callback.explosion_center_coords = neighbour.get_coordinates()
            callback.can_trigger_callbacks = False
            explosions_per_radius[radius].append(callback)

            self.scan_for_neighbour_mines(
                game_board,
                neighbour.row_index,
                neighbour.column_index,
                processed_mines,
                explosions_per_radius,
            )

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
