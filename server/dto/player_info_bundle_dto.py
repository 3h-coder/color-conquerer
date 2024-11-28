from dataclasses import dataclass

from dto.base_dto import BaseDto
from dto.partial_player_game_info_dto import PartialPlayerGameInfoDto


@dataclass
class PlayerGameInfoBundleDto(BaseDto):
    player1GameInfo: PartialPlayerGameInfoDto
    player2GameInfo: PartialPlayerGameInfoDto
