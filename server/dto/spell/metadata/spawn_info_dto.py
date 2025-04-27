from dataclasses import dataclass

from dto.base_dto import BaseDto
from dto.misc.coordinates_dto import CoordinatesDto


@dataclass
class SpawnInfoDto(BaseDto):
    coordinates: list[CoordinatesDto]
