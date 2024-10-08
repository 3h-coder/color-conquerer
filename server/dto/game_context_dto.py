from dataclasses import dataclass

from dto.base_dto import BaseDto
from dto.match_info_dto import MatchInfoDto
from dto.server_only.player_info_dto import PlayerInfoDto


@dataclass
class GameContextDto(BaseDto):
    matchInfo: MatchInfoDto
    playerInfo: PlayerInfoDto
