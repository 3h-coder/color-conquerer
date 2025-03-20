from dataclasses import dataclass

from dto.match.coordinates_dto import CoordinatesDto


@dataclass(frozen=True)
class Coordinates:
    row_index: int
    column_index: int

    def to_dto(self):
        return CoordinatesDto(self.row_index, self.column_index)

    def as_tuple(self):
        return (self.row_index, self.column_index)
