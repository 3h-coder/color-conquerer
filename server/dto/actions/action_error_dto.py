from dataclasses import dataclass

from dto.base_dto import BaseDto
from dto.misc.cell_dto import CellDto
from handlers.match_services.action_helpers.player_mode import PlayerMode


@dataclass
class ActionErrorDto(BaseDto):
    error: str
    playerMode: PlayerMode
    gameBoard: list[list[CellDto]]
