from dataclasses import dataclass

from dto.base_dto import BaseDto
from dto.queue_player_dto import QueuePlayerDto


@dataclass
class Room(BaseDto):
    id: str
    player1: QueuePlayerDto
    player2: QueuePlayerDto
    sessionIds: dict[str, str]
