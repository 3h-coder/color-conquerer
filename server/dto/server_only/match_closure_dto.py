from dataclasses import dataclass
from enum import StrEnum

from dto.base_dto import BaseDto
from game_engine.models.player import Player


class EndingReason(StrEnum):
    PLAYER_LEFT = "player left"
    PLAYER_WON = "player won"
    DRAW = "draw"
    NEVER_JOINED = "player never joined the match"


@dataclass
class MatchClosureDto(BaseDto):
    endingReason: str
    winner: Player | None  # None if draw or no winner
    loser: Player | None  # None if draw or no loser
    totalTurns: int
    actionsPerTurn: dict[int, list]
