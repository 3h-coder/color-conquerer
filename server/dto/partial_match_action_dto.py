from dataclasses import dataclass
from typing import TYPE_CHECKING

from dto.base_dto import BaseDto
from dto.coordinates_dto import CoordinatesDto

if TYPE_CHECKING:
    from dto.server_only.match_action_dto import ActionType, MatchActionDto


@dataclass
class PartialMatchActionDto(BaseDto):
    player1: bool
    type: "ActionType"
    originatingCellCoords: CoordinatesDto
    impactedCoords: tuple[CoordinatesDto]

    @staticmethod
    def from_match_action_dto(match_action_dto: "MatchActionDto"):
        if not match_action_dto:
            return None

        return PartialMatchActionDto(
            match_action_dto.player1,
            match_action_dto.type,
            match_action_dto.originatingCellCoords,
            match_action_dto.impactedCoords,
        )
