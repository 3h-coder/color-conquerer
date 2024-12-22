from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING

from dto.base_dto import BaseDto
from dto.partial_player_info_dto import PartialPlayerInfoDto

if TYPE_CHECKING:
    from dto.server_only.match_closure_dto import MatchClosureDto


@dataclass
class PartialMatchClosureDto(BaseDto):
    endingReason: str
    winner: PartialPlayerInfoDto
    loser: PartialPlayerInfoDto

    @staticmethod
    def from_match_closure_dto(match_closure_dto: "MatchClosureDto"):
        return PartialMatchClosureDto(
            endingReason=match_closure_dto.endingReason,
            winner=PartialPlayerInfoDto.from_player_info_dto(match_closure_dto.winner),
            loser=PartialPlayerInfoDto.from_player_info_dto(match_closure_dto.loser),
        )
