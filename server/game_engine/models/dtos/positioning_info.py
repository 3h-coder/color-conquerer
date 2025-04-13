from dataclasses import dataclass

from dto.spell.metadata.positioning_info_dto import PositioningInfoDto
from game_engine.models.dtos.coordinates import Coordinates


@dataclass
class PositioningInfo:
    formation_per_coordinates: dict[str, int]
    cell_formations: list[list[Coordinates]]

    def __repr__(self):
        return (
            f"<PositioningInfo(formation_per_coordinates={self.formation_per_coordinates}, "
            f"cell_formations={self.cell_formations})>"
        )

    def to_dto(self):
        return PositioningInfoDto(
            formationPerCoordinates=self.formation_per_coordinates,
            cellFormations=[
                [coord.to_dto() for coord in formation]
                for formation in self.cell_formations
            ],
        )
