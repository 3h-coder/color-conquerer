from dataclasses import dataclass
from enum import IntEnum
from dto.base_dto import BaseDto


class ActionType(IntEnum):
    CELL_MOVE = 0
    CELL_ATTACK = 1
    PLAYER_SPELL = 2


@dataclass
class MatchActionDto(BaseDto):
    fromPlayer1: bool
    isDirect: bool
    type: ActionType
    impactedCoords: list[int]
