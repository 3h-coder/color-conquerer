from dto.coordinates_dto import CoordinatesDto
from dto.match_action_dto import ActionType, MatchActionDto
from game_engine.models.actions.action import Action


class CellAction(Action):

    def __init__(
        self,
        from_player1: bool,
        impacted_coords: bool,
        originating_coords: CoordinatesDto,
        cell_id: str,
    ):
        super().__init__(from_player1, impacted_coords)
        self.originating_coords = originating_coords
        self.cell_id = cell_id

    def to_dto(self):
        return MatchActionDto(
            player1=self.from_player1,
            type=None,
            originatingCellCoords=self.originating_coords,
            impactedCoords=self.impacted_coords,
            spellId=None,
        )
