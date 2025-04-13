from dataclasses import dataclass

from dto.actions.action_metadata_dto import ActionMetadataDto
from game_engine.models.dtos.coordinates import Coordinates


@dataclass
class ActionMedatata:
    originating_coords: Coordinates
    impacted_coords: Coordinates
    # Coordinates of all the cells that died as a result of the action
    deaths: list[Coordinates]

    def __repr__(self):
        return (
            f"<ActionMetadata(originating_cell_coords={self.originating_coords}, "
            f"impacted_coords={self.impacted_coords}, "
            f"deaths={self.deaths})>"
        )

    def __eq__(self, other):
        return (
            isinstance(other, ActionMedatata)
            and other.originating_coords == self.originating_coords
            and other.impacted_coords == self.impacted_coords
            and other.deaths == self.deaths
        )

    def __hash__(self):
        return hash((self.originating_coords, self.impacted_coords))

    def to_dto(self):
        return ActionMetadataDto(
            originatingCellCoords=self.originating_coords.to_dto(),
            impactedCoords=self.impacted_coords.to_dto(),
            deaths=[coord.to_dto() for coord in self.deaths],
            positioningInfo=None,
        )

    def get_default():
        return ActionMedatata(
            originating_coords=Coordinates(-1, -1),
            impacted_coords=Coordinates(-1, -1),
            deaths=[],
        )
