from dataclasses import dataclass

from dto.base_dto import BaseDto
from dto.misc.coordinates_dto import CoordinatesDto


@dataclass
class ShieldFormationMetadataDto(BaseDto):
    # Using string keys in format "row,col" mapping to the square index
    squarePerCoordinates: dict[str, int]
    # List of squares, where each square is a list of coordinates
    squares: list[list[CoordinatesDto]]
