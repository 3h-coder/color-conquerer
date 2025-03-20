from dataclasses import dataclass
from typing import Any

from dto.base_dto import BaseDto
from dto.misc.coordinates_dto import CoordinatesDto
from dto.spell.partial_spell_dto import PartialSpellDto
from game_engine.models.actions.action_type import ActionType


@dataclass
class MatchActionDto(BaseDto):
    player1: bool
    type: ActionType
    originatingCellCoords: CoordinatesDto
    impactedCoords: CoordinatesDto
    spell: PartialSpellDto | None
    metadata: Any
