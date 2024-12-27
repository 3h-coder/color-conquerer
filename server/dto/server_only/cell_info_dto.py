from dataclasses import dataclass
from enum import IntEnum

from dto.partial_cell_info_dto import PartialCellInfoDto
from dto.server_only.player_info_dto import PlayerInfoDto


# The following states are temporary and are meant to be
# sent to the player whose turn it is to inform him of the
# possible actions he can take.
class CellState(IntEnum):
    NONE = 0
    SELECTED = 1
    CAN_BE_MOVED_INTO = 2
    CAN_BE_SPAWNED_INTO = 3
    CAN_BE_ATTACKED = 4


class CellOwner(IntEnum):
    NONE = 0
    PLAYER_1 = 1
    PLAYER_2 = 2


@dataclass
class CellInfoDto(PartialCellInfoDto):
    id: str

    def __eq__(self, other_cell):
        return (
            isinstance(other_cell, CellInfoDto)
            and self.rowIndex == other_cell.rowIndex
            and self.columnIndex == other_cell.columnIndex
            and self.id == other_cell.id
        )

    def __hash__(self):
        return hash(self.rowIndex, self.columnIndex, self.id)

    def clone(self):
        return CellInfoDto(
            owner=self.owner,
            isMaster=self.isMaster,
            rowIndex=self.rowIndex,
            columnIndex=self.columnIndex,
            state=self.state,
            id=self.id,
        )

    def set_idle(self):
        self.owner = CellOwner.NONE
        self.id = None
        self.isMaster = False

    def set_owned_by_player1(self, id: str = None):
        if self.owner == CellOwner.PLAYER_1:
            return

        from utils.id_generation_utils import generate_id

        self.owner = CellOwner.PLAYER_1
        self.id = id if id else generate_id(CellInfoDto)
        self.isMaster = False

    def set_owned_by_player2(self, id: str = None):
        if self.owner == CellOwner.PLAYER_2:
            return

        from utils.id_generation_utils import generate_id

        self.owner = CellOwner.PLAYER_2
        self.id = id if id else generate_id(CellInfoDto)
        self.isMaster = False

    def is_owned(self):
        return self.owner != CellOwner.NONE

    def belongs_to_player_1(self):
        return self.owner == CellOwner.PLAYER_1

    def belongs_to_player_2(self):
        return self.owner == CellOwner.PLAYER_2

    def belongs_to(self, player: PlayerInfoDto):
        return (
            self.owner == CellOwner.PLAYER_1
            if player.isPlayer1
            else self.owner == CellOwner.PLAYER_2
        )

    def is_hostile_to(self, other_cell: "CellInfoDto"):
        return other_cell.owner != CellOwner.NONE and other_cell.owner != self.owner

    def clear_state(self):
        self.state = CellState.NONE

    def set_selected(self):
        self.state = CellState.SELECTED

    def set_can_be_moved_into(self):
        self.state = CellState.CAN_BE_MOVED_INTO

    def set_can_be_spawned_into(self):
        self.state = CellState.CAN_BE_SPAWNED_INTO

    def set_can_be_attacked(self):
        self.state = CellState.CAN_BE_ATTACKED
