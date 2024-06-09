from dataclasses import dataclass

from dto.base_dto import BaseDto
from dto.cell_info_dto import CellInfoDto
from dto.player_info_dto import PlayerInfoDto


@dataclass
class MatchInfoDto(BaseDto):
    id: str
    boardArray: list[list[CellInfoDto]]
    player1: PlayerInfoDto
    player2: PlayerInfoDto
    currentTurn: int
    started: bool
