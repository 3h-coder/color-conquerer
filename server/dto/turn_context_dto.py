from dataclasses import dataclass

from dto.base_dto import BaseDto
from dto.cell_dto import CellDto
from dto.player_resources_bundle_dto import PlayerResourceBundleDto


@dataclass
class TurnContextDto(BaseDto):
    currentPlayerId: str
    isPlayer1Turn: bool
    remainingTimeInS: int
    durationInS: int
    notifyTurnChange: bool
    updatedBoardArray: list[list[CellDto]]
    playerResourceBundle: PlayerResourceBundleDto
