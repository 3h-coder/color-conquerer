from dataclasses import dataclass

from dto.partial_player_info_dto import PartialPlayerInfoDto
from dto.user_dto import UserDto


@dataclass
class PlayerInfoDto(PartialPlayerInfoDto):
    user: UserDto
