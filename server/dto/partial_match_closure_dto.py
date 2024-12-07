from dataclasses import dataclass
from enum import StrEnum

from dto.base_dto import BaseDto
from dto.partial_player_info_dto import PartialPlayerInfoDto


@dataclass
class PartialMatchClosureDto(BaseDto):
    endingReason: str
    winner: PartialPlayerInfoDto
    loser: PartialPlayerInfoDto

    @classmethod
    def from_match_closure_dto(cls, match_closure_dto):
        return PartialMatchClosureDto(
            endingReason=match_closure_dto.endingReason,
            winner=PartialPlayerInfoDto.from_player_info_dto(match_closure_dto.winner),
            loser=PartialPlayerInfoDto.from_player_info_dto(match_closure_dto.loser),
        )
