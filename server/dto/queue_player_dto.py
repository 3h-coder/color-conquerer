from dataclasses import dataclass

from dto.base_dto import BaseDto
from dto.user_dto import UserDto


@dataclass
class QueuePlayerDto(BaseDto):
    user: UserDto
    playerId: str

    @classmethod
    def from_dict(cls, data):
        data["user"] = UserDto.from_dict(data["user"])
        return super().from_dict(data)
