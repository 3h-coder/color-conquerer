from dataclasses import dataclass
from enum import StrEnum

from dto.base_dto import BaseDto
from dto.server_only.player_info_dto import PlayerInfoDto


class EndingReason(StrEnum):
    PLAYER_LEFT = "player left"
    PLAYER_WON = "player won"
    DRAW = "draw"
    NEVER_JOINED = "player never joined the match"


@dataclass
class MatchClosureDto(BaseDto):
    endingReason: str
    winner: PlayerInfoDto | None  # None if draw or no winner
    loser: PlayerInfoDto | None  # None if draw or no loser
    totalTurns: int
    actionsPerTurn: dict[int, list]
