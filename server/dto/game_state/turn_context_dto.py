from dataclasses import dataclass

from dto.base_dto import BaseDto
from dto.game_state.game_context_dto import GameContextDto
from dto.misc.cell_dto import CellDto
from dto.player.player_resources_bundle_dto import PlayerResourceBundleDto


@dataclass
class TurnContextDto(BaseDto):
    currentPlayerId: str
    isPlayer1Turn: bool
    remainingTimeInS: int
    durationInS: int
    notifyTurnChange: bool
    gameContext: GameContextDto
