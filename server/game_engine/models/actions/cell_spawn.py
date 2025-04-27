from dataclasses import dataclass

from dto.actions.match_action_dto import ActionType, MatchActionDto
from game_engine.models.actions.action import Action
from game_engine.models.actions.callbacks.action_callback_id import ActionCallBackId
from game_engine.models.actions.hooks.mana_bubble_hook import ManaBubbleHook
from game_engine.models.cell.cell import Cell
from game_engine.models.dtos.coordinates import Coordinates
from game_engine.models.game_board import GameBoard
from game_engine.models.match_context import MatchContext


@dataclass
class CellSpawn(Action):
    """
    Represents a friendly/enemy cell being summoned.
    """

    DEFAULT_MANA_COST = 1
    HOOKS = {ManaBubbleHook()}
    CALLBACKS = {ActionCallBackId.MINE_EXPLOSION}

    def __init__(self, from_player1: bool, impacted_coords: Coordinates):
        super().__init__(
            from_player1=from_player1,
            impacted_coords=impacted_coords,
        )

    def __eq__(self, other):
        return (
            isinstance(other, CellSpawn)
            and other.from_player1 == self.from_player1
            and other.metadata == self.metadata
        )

    def __hash__(self):
        return hash((self.from_player1, self.metadata))

    def __repr__(self):
        return (
            f"<CellSpawn(from_player1={self.from_player1}, "
            f"mana_cost={self.mana_cost}, "
            f"metadata={self.metadata}, "
            f"callbacks_to_trigger={self._callbacks_to_trigger})>"
        )

    def to_dto(self):
        return MatchActionDto(
            player1=self.from_player1,
            type=ActionType.CELL_SPAWN,
            spell=None,
            metadata=self.metadata.to_dto(),
            specificMetadata=None,
        )

    @staticmethod
    def create(from_player1: bool, row_index: int, column_index: int):
        return CellSpawn(
            from_player1=from_player1,
            impacted_coords=Coordinates(row_index, column_index),
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

    @Action.trigger_hooks_and_check_callbacks
    def apply(self, match_context: MatchContext):
        """
        Spawns a cell at the given coordinates for the given player.
        """
        target_coords = self.metadata.impacted_coords
        match_context.game_board.spawn_cell(target_coords, self.from_player1)
