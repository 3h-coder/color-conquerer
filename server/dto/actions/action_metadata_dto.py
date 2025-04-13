from dataclasses import dataclass

from dto.base_dto import BaseDto
from dto.misc.coordinates_dto import CoordinatesDto
from dto.spell.metadata.positioning_info_dto import PositioningInfoDto


@dataclass
class ActionMetadataDto(BaseDto):
    originatingCellCoords: CoordinatesDto
    impactedCoords: CoordinatesDto
    deaths: list[CoordinatesDto]
    positioningInfo: PositioningInfoDto | None
