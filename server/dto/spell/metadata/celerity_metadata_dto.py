from dataclasses import dataclass

from dto.base_dto import BaseDto
from dto.misc.coordinates_dto import CoordinatesDto


@dataclass
class CelerityMetadataDto(BaseDto):
    # Using string keys in format "row,col" mapping to the diagonal index
    diagonalPerCoordinates: dict[str, int]
    # List of diagonals, where each diagonal is a list of coordinates
    diagonals: list[list[CoordinatesDto]]
