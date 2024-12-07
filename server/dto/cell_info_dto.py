from dataclasses import dataclass
from enum import IntEnum

from dto.base_dto import BaseDto


class CellState(IntEnum):
    IDLE = 0
    CAPTURED = 1
    FROZEN = 2


@dataclass
class CellInfoDto(BaseDto):
    owner: int
    isMaster: bool
    rowIndex: int
    columnIndex: int
    state: CellState
