from dataclasses import dataclass

from dto.cell_dto import CellDto
from game_engine.models.cell.cell_owner import CellOwner
from game_engine.models.cell.cell_state import CellState
from game_engine.models.cell.cell_transient_state import CellTransientState
from game_engine.models.player import Player


@dataclass
class Cell:
    owner: CellOwner
    is_master: bool
    row_index: int
    column_index: int
    state: CellState
    transient_state: CellTransientState
    id: str

    def __eq__(self, other_cell):
        return (
            isinstance(other_cell, Cell)
            and self.row_index == other_cell.row_index
            and self.column_index == other_cell.column_index
            and self.id == other_cell.id
        )

    def __hash__(self):
        return hash(self.row_index, self.column_index, self.id)

    def __str__(self):
        return (
            f"Cell(owner: {self.owner}, is_master: {self.is_master}, "
            f"row_index: {self.row_index}, column_index: {self.column_index}, "
            f"state: {self.state}, transient_state: {self.transient_state}, id: {self.id})"
        )

    def to_dto(self):
        return CellDto(
            self.owner,
            self.is_master,
            self.row_index,
            self.column_index,
            self.state,
            self.transient_state,
        )

    def clone(self):
        return Cell(
            owner=self.owner,
            is_master=self.is_master,
            row_index=self.row_index,
            column_index=self.column_index,
            state=self.state,
            transient_state=self.transient_state,
            id=self.id,
        )

    @staticmethod
    def get_default_idle_cell(row_index: int, col_index: int):
        return Cell(
            owner=CellOwner.NONE,
            is_master=False,
            row_index=row_index,
            column_index=col_index,
            state=CellState.NONE,
            transient_state=CellTransientState.NONE,
            id=None,
        )

    def set_idle(self):
        self.owner = CellOwner.NONE
        self.id = None
        self.is_master = False
        self.state = CellState.NONE
        self.transient_state = CellTransientState.NONE

    def set_owned_by_player1(self, id: str = None):
        if self.owner == CellOwner.PLAYER_1:
            return

        from utils.id_generation_utils import generate_id

        self.owner = CellOwner.PLAYER_1
        self.id = id if id else generate_id(Cell)
        self.is_master = False

    def set_owned_by_player2(self, id: str = None):
        if self.owner == CellOwner.PLAYER_2:
            return

        from utils.id_generation_utils import generate_id

        self.owner = CellOwner.PLAYER_2
        self.id = id if id else generate_id(Cell)
        self.is_master = False

    def is_owned(self):
        return self.owner != CellOwner.NONE

    def belongs_to_player_1(self):
        return self.owner == CellOwner.PLAYER_1

    def belongs_to_player_2(self):
        return self.owner == CellOwner.PLAYER_2

    def belongs_to(self, player: Player):
        return (
            self.owner == CellOwner.PLAYER_1
            if player.is_player_1
            else self.owner == CellOwner.PLAYER_2
        )

    def is_hostile_to(self, other_cell: "Cell"):
        return (
            self.owner != CellOwner.NONE
            and other_cell.owner != CellOwner.NONE
            and other_cell.owner != self.owner
        )

    def is_freshly_spawned(self):
        return self.state == CellState.FRESHLY_SPAWNED

    def is_mana_bubble(self):
        return self.state == CellState.MANA_BUBBLE

    def clear_state(self):
        self.state = CellState.NONE

    def set_selected(self):
        self.transient_state = CellTransientState.SELECTED

    def set_can_be_moved_into(self):
        self.transient_state = CellTransientState.CAN_BE_MOVED_INTO

    def set_can_be_spawned_into(self):
        self.transient_state = CellTransientState.CAN_BE_SPAWNED_INTO

    def set_can_be_attacked(self):
        self.transient_state = CellTransientState.CAN_BE_ATTACKED

    def set_can_be_spell_targetted(self):
        self.transient_state = CellTransientState.CAN_BE_SPELL_TARGETTED

    def set_freshly_spawned(self):
        self.state = CellState.FRESHLY_SPAWNED

    def set_as_mana_bubble(self):
        self.state = CellState.MANA_BUBBLE

    def set_as_mine_trap(self):
        self.state = CellState.MINE_TRAP
