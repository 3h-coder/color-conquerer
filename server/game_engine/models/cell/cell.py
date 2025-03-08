from dataclasses import dataclass

from dto.cell_dto import CellDto
from dto.coordinates_dto import CoordinatesDto
from game_engine.models.cell.cell_hidden_state import CellHiddenState
from game_engine.models.cell.cell_hidden_state_info import CellHiddenStateInfo
from game_engine.models.cell.cell_owner import CellOwner
from game_engine.models.cell.cell_state import CellState
from game_engine.models.cell.cell_transient_state import CellTransientState
from game_engine.models.player import Player
from game_engine.models.player_resources import PlayerResources


class Cell:
    def __init__(
        self,
        owner: CellOwner,
        is_master: bool,
        row_index: int,
        column_index: int,
        state: CellState,
        hidden_state_info: CellHiddenStateInfo,
        transient_state: CellTransientState,
        id: str,
    ):
        self.owner = owner
        self.is_master = is_master
        self.row_index = row_index
        self.column_index = column_index
        self.state = state
        self.hidden_state_info = hidden_state_info
        self.transient_state = transient_state
        self.id = id

    def __eq__(self, other_cell):
        return (
            isinstance(other_cell, Cell)
            and self.row_index == other_cell.row_index
            and self.column_index == other_cell.column_index
            and self.id == other_cell.id
        )

    def __hash__(self):
        return hash(self.row_index, self.column_index, self.id)

    def __repr__(self):
        return (
            f"<Cell(owner={self.owner!r}, is_master={self.is_master!r}, "
            f"row_index={self.row_index!r}, column_index={self.column_index!r}, "
            f"state={self.state!r}, hidden_state_info={self.hidden_state_info!r}, "
            f"transient_state={self.transient_state!r}, id={self.id!r})>"
        )

    def to_dto(self, for_player1: bool | None):
        return CellDto(
            owner=self.owner,
            isMaster=self.is_master,
            rowIndex=self.row_index,
            columnIndex=self.column_index,
            state=self.state,
            hiddenState=self._get_hidden_state(for_player1),
            transientState=self.transient_state,
        )

    def clone(self):
        return Cell(
            owner=self.owner,
            is_master=self.is_master,
            row_index=self.row_index,
            column_index=self.column_index,
            state=self.state,
            hidden_state_info=self.hidden_state_info,
            transient_state=self.transient_state,
            id=self.id,
        )

    def get_coordinates(self):
        return CoordinatesDto(self.row_index, self.column_index)

    @staticmethod
    def get_default_idle_cell(row_index: int, col_index: int):
        return Cell(
            owner=CellOwner.NONE,
            is_master=False,
            row_index=row_index,
            column_index=col_index,
            state=CellState.NONE,
            # hidden_state_info=CellHiddenStateInfo.default(),
            hidden_state_info=CellHiddenStateInfo(
                state=CellHiddenState.MINE_TRAP, visible_to=CellOwner.BOTH
            ),
            transient_state=CellTransientState.NONE,
            id=None,
        )

    def set_idle(self):
        self.owner = CellOwner.NONE
        self.id = None
        self.is_master = False
        self.state = CellState.NONE
        self.hidden_state_info = CellHiddenStateInfo.default()
        self.transient_state = CellTransientState.NONE

    def kill(self):
        if not self.is_owned():
            return

        self.owner = CellOwner.NONE
        self.id = None
        self.is_master = False
        self.state = CellState.NONE

    def damage(
        self, player1_resources: PlayerResources, player2_resources: PlayerResources
    ):
        """
        Damages a cell, affecting the player's hp if it's a master cell, destroying it otherwise.
        """
        if self.belongs_to_player_1() and self.is_master:
            player1_resources.current_hp -= 1
            if player1_resources.current_hp <= 0:
                self.kill()

        elif self.belongs_to_player_2() and self.is_master:
            player2_resources.current_hp -= 1
            if player2_resources.current_hp <= 0:
                self.kill()

        else:
            self.kill()

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

    def is_mine_trap(self):
        return self.hidden_state_info.is_mine_trap()

    def has_hidden_state(self):
        return self.hidden_state_info.state != CellHiddenState.NONE

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

    def set_as_mine_trap(self, owner: CellOwner):
        visible_to = owner

        if self.hidden_state_info.is_mine_trap():
            if self.hidden_state_info.is_visible_to_both():
                visible_to = CellOwner.BOTH
            elif (
                self.hidden_state_info.is_visible_to_player1()
                and owner == CellOwner.PLAYER_2
            ):
                visible_to = CellOwner.BOTH
            elif (
                self.hidden_state_info.is_visible_to_player2()
                and owner == CellOwner.PLAYER_1
            ):
                visible_to = CellOwner.BOTH

        self.hidden_state_info = CellHiddenStateInfo(
            state=CellHiddenState.MINE_TRAP,
            visible_to=visible_to,
        )

    def _get_hidden_state(self, for_player1: bool | None):
        hidden_state = CellHiddenState.NONE
        if (
            self.hidden_state_info.is_visible_to_both()
            or (for_player1 is True and self.hidden_state_info.is_visible_to_player1())
            or (for_player1 is False and self.hidden_state_info.is_visible_to_player2())
        ):
            hidden_state = self.hidden_state_info.state

        return hidden_state
