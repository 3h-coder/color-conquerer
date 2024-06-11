from dataclasses import dataclass

from dto.base_dto import BaseDto
from dto.queue_register_dto import QueueRegisterDto


@dataclass
class RoomDto(BaseDto):
    id: str
    player1: QueueRegisterDto
    player2: QueueRegisterDto
