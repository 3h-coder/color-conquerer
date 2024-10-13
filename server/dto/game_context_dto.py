from dataclasses import dataclass

from dto.base_dto import BaseDto
from dto.partial_match_info_dto import PartialMatchInfoDto
from dto.partial_player_info_dto import PartialPlayerInfoDto


@dataclass
class GameContextDto(BaseDto):
    matchInfo: PartialMatchInfoDto
    playerInfo: PartialPlayerInfoDto
