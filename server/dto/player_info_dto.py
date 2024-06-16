from dataclasses import dataclass

from dto.base_dto import BaseDto
from dto.user_dto import UserDto


@dataclass
class PlayerInfoDto(BaseDto):
    user: UserDto
    playerId: str
    isPlayer1: bool
