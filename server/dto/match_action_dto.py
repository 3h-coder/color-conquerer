from dataclasses import dataclass

from dto.base_dto import BaseDto
from dto.coordinates_dto import CoordinatesDto
from dto.partial_spell_dto import PartialSpellDto
from game_engine.models.actions.action_type import ActionType


@dataclass
class MatchActionDto(BaseDto):
    player1: bool
    type: ActionType
    originatingCellCoords: CoordinatesDto
    impactedCoords: list[CoordinatesDto]
    spell: PartialSpellDto | None
