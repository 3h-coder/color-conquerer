from dataclasses import dataclass

from dto.partial_match_info_dto import PartialMatchInfoDto
from dto.server_only.player_info_dto import PlayerInfoDto


# TODO: split between client and server match info
@dataclass
class MatchInfoDto(PartialMatchInfoDto):
    player1: PlayerInfoDto
    player2: PlayerInfoDto
