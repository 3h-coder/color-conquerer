import random
from typing import TYPE_CHECKING

from constants.game_constants import SPELLS_MANA_COST
from dto.spell.metadata.spawn_info_dto import SpawnInfoDto
from game_engine.models.cell.cell_owner import CellOwner
from game_engine.models.dtos.coordinates import Coordinates
from game_engine.models.spells.abstract.spell import Spell
from game_engine.models.spells.spell_id import SpellId

if TYPE_CHECKING:
    from game_engine.models.game_board import GameBoard
    from game_engine.models.match.match_context import MatchContext


class AmbushSpell(Spell):
    ID = SpellId.AMBUSH
    NAME = "Ambush"
    DESCRIPTION = "Select an enemy cell. Randomly spawn two friendly cells next to it. If the target is on the opponent's side, spawn an extra cell."
    MANA_COST = SPELLS_MANA_COST.get(ID, 0)
    CONDITION_NOT_MET_ERROR_MESSAGE = "No enemy cell to ambush"
    INVALID_SELECTION_ERROR_MESSAGE = "Cannot ambush this cell"

    MAX_SPAWNED_CELLS = 2

    def __init__(self):
        super().__init__()
        self._spawn_coordinates: list[Coordinates] = []

    def get_possible_targets(self, transient_board: "GameBoard", from_player1: bool):
        possible_targets: list[Coordinates] = []
        enemy_cells = transient_board.get_cells_owned_by_player(
            player1=not from_player1
        )

        for cell in enemy_cells:
            if transient_board.get_idle_neighbours(cell.row_index, cell.column_index):
                cell.set_can_be_spell_targetted()
                possible_targets.append(cell.get_coordinates())

        return possible_targets

    def invoke(
        self,
        coordinates: Coordinates,
        match_context: "MatchContext",
        invocator: CellOwner,
    ):
        from game_engine.models.actions.cell_spawn import CellSpawn

        board = match_context.game_board
        idle_neighbours = board.get_idle_neighbours(
            coordinates.row_index, coordinates.column_index
        )

        number_of_cells_to_spawn = self.MAX_SPAWNED_CELLS
        if coordinates.is_on_player_side(
            of_player1=True if invocator == CellOwner.PLAYER_2 else False
        ):
            number_of_cells_to_spawn += 1

        selected_neighbours = random.sample(
            idle_neighbours, min(number_of_cells_to_spawn, len(idle_neighbours))
        )
        self._spawn_coordinates = []

        for neighbour in selected_neighbours:
            coordinates = neighbour.get_coordinates()
            cell_spawn = CellSpawn.create(
                from_player1=invocator == CellOwner.PLAYER_1,
                row_index=coordinates.row_index,
                column_index=coordinates.column_index,
            )
            cell_spawn.apply(match_context)
            self._callbacks_to_trigger_for_parent_spell_casting.extend(
                cell_spawn._callbacks_to_trigger
            )
            self._spawn_coordinates.append(coordinates)

    def get_specific_metadata_dto(self):
        return self._get_spawn_info_dto()

    def _get_spawn_info_dto(self):
        return SpawnInfoDto(
            coordinates=[coord.to_dto() for coord in self._spawn_coordinates]
        )
