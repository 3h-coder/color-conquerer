from dataclasses import dataclass

from dto.base_dto import BaseDto


@dataclass
class RoomDto(BaseDto):
    id: str
    player1id: str
    player2id: str
