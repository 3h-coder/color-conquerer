from dataclasses import dataclass
from enum import IntEnum

from dto.partial_cell_info_dto import PartialCellInfoDto
from dto.server_only.player_info_dto import PlayerInfoDto


class CellState(IntEnum):
    AVAILABLE = 0
    UNAVAILABLE = 1


class CellOwner(IntEnum):
    NONE = 0
    PLAYER_1 = 1
    PLAYER_2 = 2


@dataclass
class CellInfoDto(PartialCellInfoDto):
    id: str
    state: CellState

    def __eq__(self, other_cell):
        return (
            isinstance(other_cell, CellInfoDto)
            and self.rowIndex == other_cell.rowIndex
            and self.columnIndex == other_cell.columnIndex
            and self.id == other_cell.id
        )

    def __hash__(self):
        return hash(self.rowIndex, self.columnIndex, self.id)

    def set_idle(self):
        self.owner = CellOwner.NONE
        self.id = None

    def set_owned_by_player1(self):
        from utils.id_generation_utils import generate_id

        self.owner = CellOwner.PLAYER_1
        self.id = generate_id(CellInfoDto)

    def set_owned_by_player2(self):
        from utils.id_generation_utils import generate_id

        self.owner = CellOwner.PLAYER_2
        generate_id(CellInfoDto)

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
