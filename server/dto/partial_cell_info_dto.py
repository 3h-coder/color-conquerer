from dataclasses import dataclass
from enum import IntEnum
from typing import TYPE_CHECKING

from dto.base_dto import BaseDto

if TYPE_CHECKING:
    from dto.server_only.cell_info_dto import (
        CellInfoDto,
        CellOwner,
        CellTransientState,
        CellState,
    )


@dataclass
class PartialCellInfoDto(BaseDto):
    owner: "CellOwner"
    isMaster: bool
    rowIndex: int
    columnIndex: int
    state: "CellState"
    transientState: "CellTransientState"

    @staticmethod
    def from_cell_info_dto(cell_info_dto: "CellInfoDto"):
        return PartialCellInfoDto(
            cell_info_dto.owner,
            cell_info_dto.isMaster,
            cell_info_dto.rowIndex,
            cell_info_dto.columnIndex,
            cell_info_dto.state,
            cell_info_dto.transientState,
        )
