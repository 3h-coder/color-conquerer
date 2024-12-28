from dataclasses import dataclass

from dto.base_dto import BaseDto
from dto.partial_cell_info_dto import PartialCellInfoDto
from dto.player_info_bundle_dto import PlayerGameInfoBundleDto


@dataclass
class TurnInfoDto(BaseDto):
    currentPlayerId: str
    isPlayer1Turn: bool
    durationInS: int
    totalTurnDurationInS: int
    notifyTurnChange: bool
    playerGameInfoBundle: PlayerGameInfoBundleDto
    updatedBoardArray: list[list[PartialCellInfoDto]]
