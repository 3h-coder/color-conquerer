from dataclasses import dataclass

from dto.base_dto import BaseDto
from dto.match_action_dto import MatchActionDto


@dataclass
class PossibleActionsDto(BaseDto):
    possibleActions: list[MatchActionDto]
