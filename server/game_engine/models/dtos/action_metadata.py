from dataclasses import dataclass

from dto.actions.action_metadata_dto import ActionMetadataDto
from game_engine.models.dtos.coordinates import Coordinates


@dataclass
class ActionMedatata:
    originating_coords: Coordinates
    impacted_coords: Coordinates

    def __repr__(self):
        return (
            f"<ActionMetadata(originating_cell_coords={self.originating_coords}, "
            f"impacted_coords={self.impacted_coords}>"
        )

    def __eq__(self, value):
        return (
            isinstance(value, ActionMedatata)
            and value.originating_coords == self.originating_coords
            and value.impacted_coords == self.impacted_coords
        )

    def __hash__(self):
        return hash((self.originating_coords, self.impacted_coords))

    def to_dto(self):
        return ActionMetadataDto(
            originatingCellCoords=self.originating_coords.to_dto(),
            impactedCoords=self.impacted_coords.to_dto(),
            positioningInfo=None,
        )

    def get_default():
        return ActionMedatata(
            originating_coords=Coordinates(-1, -1),
            impacted_coords=Coordinates(-1, -1),
        )
