from dto.actions.match_action_dto import MatchActionDto
from game_engine.models.actions.action import Action
from game_engine.models.dtos.coordinates import Coordinates


class CellAction(Action):

    def __init__(
        self,
        from_player1: bool,
        impacted_coords: Coordinates,
        originating_coords: Coordinates,
        cell_id: str,
    ):
        super().__init__(from_player1, impacted_coords)
        self.cell_id = cell_id
        metadata = self.metadata
        metadata.originating_coords = originating_coords

    def to_dto(self):
        return MatchActionDto(
            player1=self.from_player1,
            type=None,  # meant to be set in subclasses
            spell=None,  # meant to be set in subclasses
            metadata=self.metadata.to_dto(),
            specificMetadata=None,  # meant to be set in subclasses
        )
