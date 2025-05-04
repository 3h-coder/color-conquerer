from dataclasses import dataclass

from dto.base_dto import BaseDto


@dataclass
class PlayerSessionDto(BaseDto):
    playerId: str
    userId: str
    isPlayer1: bool
