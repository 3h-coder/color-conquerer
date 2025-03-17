from dataclasses import dataclass

from dto.base_dto import BaseDto


@dataclass
class CoordinatesDto(BaseDto):
    rowIndex: int
    columnIndex: int
