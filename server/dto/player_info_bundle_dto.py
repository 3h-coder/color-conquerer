from dataclasses import dataclass

from dto.base_dto import BaseDto
from dto.partial_player_game_info_dto import PartialPlayerGameInfoDto
from dto.partial_player_info_dto import PartialPlayerInfoDto
from dto.player_game_info_dto import PlayerGameInfoDto
from dto.user_dto import UserDto


@dataclass
class PlayerInfoBundleDto(BaseDto):
    playerInfo: PartialPlayerInfoDto
    playerGameInfo: PlayerGameInfoDto
    opponentGameInfo: PartialPlayerGameInfoDto
