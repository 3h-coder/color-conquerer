from dataclasses import dataclass

from dto.base_dto import BaseDto
from dto.coordinates_dto import CoordinatesDto
from dto.game_context_dto import GameContextDto
from dto.match_action_dto import MatchActionDto
from dto.partial_spell_dto import PartialSpellDto
from game_engine.models.actions.callbacks.action_callback_id import ActionCallBackId


@dataclass
class ActionCallbackDto(BaseDto):
    id: int
    parentAction: MatchActionDto
    parentCallbackId: ActionCallBackId
    spellCause: PartialSpellDto | None
    impactedCoords: list[CoordinatesDto] | None
    updatedGameContext: GameContextDto
