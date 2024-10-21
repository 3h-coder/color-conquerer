from dataclasses import dataclass

from dto.base_dto import BaseDto


@dataclass
class PartialPlayerInfoDto(BaseDto):
    playerId: str
    isPlayer1: bool

    @classmethod
    def from_player_info_dto(cls, player_info_dto):
        return PartialPlayerInfoDto(player_info_dto.playerId, player_info_dto.isPlayer1)
