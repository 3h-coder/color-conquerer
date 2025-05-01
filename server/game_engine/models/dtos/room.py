from dataclasses import dataclass

from dto.player.queue_player_dto import QueuePlayerDto
from game_engine.models.player.player import Player


@dataclass
class Room:
    id: str
    player1_queue_dto: QueuePlayerDto
    player2_queue_dto: QueuePlayerDto
    player1_room_id: str
    player2_room_id: str
    session_ids: dict[str, str]
