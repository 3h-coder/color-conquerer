from dataclasses import dataclass

from dto.base_dto import BaseDto
from dto.player.player_dto import PlayerDto


@dataclass
class MatchClosureDto(BaseDto):
    endingReason: int
    winner: PlayerDto
    loser: PlayerDto
