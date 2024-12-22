from dataclasses import dataclass
from typing import TYPE_CHECKING

from dto.base_dto import BaseDto

if TYPE_CHECKING:
    from dto.server_only.cell_info_dto import CellInfoDto, CellOwner


@dataclass
class PartialCellInfoDto(BaseDto):
    owner: "CellOwner"
    isMaster: bool
    rowIndex: int
    columnIndex: int

    @classmethod
    def from_cell_info_dto(cls, cell_info_dto: "CellInfoDto"):
        return PartialCellInfoDto(
            cell_info_dto.owner,
            cell_info_dto.isMaster,
            cell_info_dto.rowIndex,
            cell_info_dto.columnIndex,
        )
