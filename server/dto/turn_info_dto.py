from dataclasses import dataclass

from dto.base_dto import BaseDto
from dto.cell_dto import CellDto
from dto.player_info_bundle_dto import PlayerGameInfoBundleDto


@dataclass
class TurnInfoDto(BaseDto):
    currentPlayerId: str
    isPlayer1Turn: bool
    durationInS: int
    totalTurnDurationInS: int
    notifyTurnChange: bool
    playerGameInfoBundle: PlayerGameInfoBundleDto
    updatedBoardArray: list[list[CellDto]]
