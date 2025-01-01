from dataclasses import dataclass
from typing import TYPE_CHECKING

from dto.base_dto import BaseDto

if TYPE_CHECKING:
    from dto.server_only.player_info_dto import PlayerInfoDto


@dataclass
class PartialPlayerInfoDto(BaseDto):
    playerId: str
    isPlayer1: bool

    @staticmethod
    def from_player_info_dto(player_info_dto: "PlayerInfoDto"):
        if player_info_dto is None:
            return None

        return PartialPlayerInfoDto(player_info_dto.playerId, player_info_dto.isPlayer1)
