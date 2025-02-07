from dataclasses import dataclass

from dto.player_resources_dto import PlayerResourcesDto


@dataclass
class PlayerResourceBundleDto:
    player1Resources: PlayerResourcesDto
    player2Resources: PlayerResourcesDto
