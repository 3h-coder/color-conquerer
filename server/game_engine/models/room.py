from dataclasses import dataclass

from dto.queue_player_dto import QueuePlayerDto
from game_engine.models.player import Player


@dataclass
class Room:
    id: str
    player1_queue_dto: QueuePlayerDto
    player2_queue_dto: QueuePlayerDto
    session_ids: dict[str, str]
