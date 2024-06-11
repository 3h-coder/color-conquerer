from dataclasses import dataclass

from dto.base_dto import BaseDto
from dto.user_dto import UserDto


@dataclass
class QueueRegisterDto(BaseDto):
    user: UserDto
    playerId: str
