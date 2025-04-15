from dataclasses import dataclass

from dto.misc.coordinates_dto import CoordinatesDto


@dataclass(frozen=True)
class Coordinates:
    row_index: int
    column_index: int

    def to_dto(self):
        return CoordinatesDto(self.row_index, self.column_index)

    def as_tuple(self):
        return (self.row_index, self.column_index)

    def is_neighbour(self, other: "Coordinates") -> bool:
        """
        Check if the two coordinates are neighbours.
        """
        return (
            abs(self.row_index - other.row_index) <= 1
            and abs(self.column_index - other.column_index) <= 1
        )
