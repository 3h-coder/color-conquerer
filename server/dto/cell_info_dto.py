from dataclasses import dataclass

from dto.base_dto import BaseDto


@dataclass
class CellInfoDto(BaseDto):
    owner: int
    rowIndex: int
    columnIndex: int
    state: str
