from dataclasses import dataclass

from dto.base_dto import BaseDto
from dto.misc.coordinates_dto import CoordinatesDto


@dataclass
class PositioningMetadataDto(BaseDto):
    # Using string keys in format "row,col" mapping to the formation index
    formationPerCoordinates: dict[str, int]
    # Represents any specific cell formation, such as a square, a line, etc.
    cellFormations: list[list[CoordinatesDto]]
