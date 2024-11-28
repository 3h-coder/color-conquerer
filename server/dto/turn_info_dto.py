from dataclasses import dataclass

from dto.base_dto import BaseDto
from dto.player_info_bundle_dto import PlayerGameInfoBundleDto


@dataclass
class TurnInfoDto(BaseDto):
    currentPlayerId: str
    isPlayer1Turn: bool
    durationInS: int
    playerInfoBundle: PlayerGameInfoBundleDto
    notifyTurnChange: bool
