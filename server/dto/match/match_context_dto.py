from dataclasses import dataclass

from dto.base_dto import BaseDto
from dto.misc.cell_dto import CellDto
from dto.player.player_dto import PlayerDto


@dataclass
class MatchContextDto(BaseDto):
    id: str
    roomId: str
    boardArray: list[list[CellDto]]
    currentTurn: int
    player1: PlayerDto
    player2: PlayerDto
