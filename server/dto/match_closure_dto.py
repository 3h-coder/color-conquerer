from dataclasses import dataclass
from enum import StrEnum

from dto.base_dto import BaseDto
from dto.player_info_dto import PlayerInfoDto


class EndingReason(StrEnum):
    PLAYER_LEFT = "player left"
    PLAYER_WON = "player won"
    DRAW = "draw"
    NEVER_JOINED = "player never joined the match"


@dataclass
class MatchClosureDto(BaseDto):
    endingReason: str
    winner: PlayerInfoDto
    loser: PlayerInfoDto
    # TODO: maybe add more stats
