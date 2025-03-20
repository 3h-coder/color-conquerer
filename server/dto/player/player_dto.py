from dataclasses import dataclass

from dto.base_dto import BaseDto
from dto.player.player_resources_dto import PlayerResourcesDto


@dataclass
class PlayerDto(BaseDto):
    playerId: str
    isPlayer1: bool
