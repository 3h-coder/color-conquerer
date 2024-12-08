from dataclasses import dataclass
from enum import IntEnum

from dto.base_dto import BaseDto


class CellState(IntEnum):
    IDLE = 0
    OWNED = 1


class CellOwner(IntEnum):
    NONE = 0
    PLAYER_1 = 1
    PLAYER_2 = 2


@dataclass
class CellInfoDto(BaseDto):
    owner: CellOwner
    isMaster: bool
    rowIndex: int
    columnIndex: int
    state: CellState

    def set_owned_by_player1(self):
        self.state = CellState.OWNED
        self.owner = CellOwner.PLAYER_1

    def set_owned_by_player2(self):
        self.state = CellState.OWNED
        self.owner = CellOwner.PLAYER_2

    def is_owned(self):
        return self.state == CellState.OWNED

    def is_hostile_to(self, other_cell: "CellInfoDto"):
        return other_cell.owner != CellOwner.NONE and other_cell.owner != self.owner
