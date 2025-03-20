from dataclasses import dataclass

from dto.actions.match_action_dto import MatchActionDto
from dto.base_dto import BaseDto
from dto.game_state.game_context_dto import GameContextDto
from dto.match.coordinates_dto import CoordinatesDto
from dto.spell.partial_spell_dto import PartialSpellDto
from game_engine.models.actions.callbacks.action_callback_id import ActionCallBackId


@dataclass
class ActionCallbackDto(BaseDto):
    id: int
    parentAction: MatchActionDto
    parentCallbackId: ActionCallBackId
    spellCause: PartialSpellDto | None
    impactedCoords: CoordinatesDto | None
    updatedGameContext: GameContextDto
