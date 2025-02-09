from dataclasses import dataclass

from dto.base_dto import BaseDto
from dto.coordinates_dto import CoordinatesDto
from game_engine.models.actions.action_type import ActionType
from game_engine.models.spells.spell import Spell


@dataclass
class MatchActionDto(BaseDto):
    player1: bool
    type: ActionType
    originatingCellCoords: CoordinatesDto
    impactedCoords: CoordinatesDto
    spellId: int
