from dataclasses import dataclass

from dto.actions.action_metadata_dto import ActionMetadataDto
from game_engine.models.dtos.coordinates import Coordinates
from game_engine.models.dtos.positioning_info import PositioningInfo


@dataclass
class ActionMedatata:
    originating_coords: Coordinates
    impacted_coords: Coordinates
    positioning_info: PositioningInfo

    def __repr__(self):
        return (
            f"<ActionMetadata(originating_cell_coords={self.originating_coords}, "
            f"impacted_coords={self.impacted_coords}, "
            f"positioning_info={self.positioning_info})>"
        )

    def __eq__(self, value):
        return (
            isinstance(value, ActionMedatata)
            and value.originating_coords == self.originating_coords
            and value.impacted_coords == self.impacted_coords
            and value.positioning_info == self.positioning_info
        )

    def __hash__(self):
        return hash(
            (self.originating_coords, self.impacted_coords, self.positioning_info)
        )

    def to_dto(self):
        return ActionMetadataDto(
            originating_coords=self.originating_coords.to_dto(),
            impacted_coords=self.impacted_coords.to_dto(),
            positioning_info=self.positioning_info.to_dto(),
        )

    def get_default():
        return ActionMedatata(
            originating_coords=Coordinates(-1, -1),
            impacted_coords=Coordinates(-1, -1),
            positioning_info=PositioningInfo(),
        )
