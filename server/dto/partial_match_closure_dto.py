from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING

from dto.base_dto import BaseDto
from dto.player_dto import PlayerDto

if TYPE_CHECKING:
    from dto.server_only.match_closure_dto import MatchClosureDto


@dataclass
class PartialMatchClosureDto(BaseDto):
    endingReason: str
    winner: PlayerDto
    loser: PlayerDto

    @staticmethod
    def from_match_closure_dto(match_closure_dto: "MatchClosureDto"):
        return PartialMatchClosureDto(
            endingReason=match_closure_dto.endingReason,
            winner=match_closure_dto.winner.to_dto(),
            loser=match_closure_dto.loser.to_dto(),
        )
