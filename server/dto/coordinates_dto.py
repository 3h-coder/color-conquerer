from dataclasses import dataclass

from dto.base_dto import BaseDto


@dataclass
class CoordinatesDto(BaseDto):
    rowIndex: int
    columnIndex: int

    def __eq__(self, other):
        if not isinstance(other, CoordinatesDto):
            return False
        return self.rowIndex == other.rowIndex and self.columnIndex == other.columnIndex

    def __hash__(self):
        return hash((self.rowIndex, self.columnIndex))
