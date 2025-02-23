from dataclasses import dataclass

from dto.base_dto import BaseDto
from dto.game_context_dto import GameContextDto
from dto.match_action_dto import MatchActionDto
from dto.partial_spell_dto import PartialSpellDto


@dataclass
class ActionCallbackDto(BaseDto):
    id: int
    parentAction: MatchActionDto
    spellCause: PartialSpellDto | None
    updatedGameContext: GameContextDto
