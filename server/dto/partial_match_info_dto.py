from dataclasses import dataclass

from dto.base_dto import BaseDto
from dto.cell_info_dto import CellInfoDto


@dataclass
class PartialMatchInfoDto(BaseDto):
    id: str
    roomId: str
    boardArray: list[list[CellInfoDto]]
    currentTurn: int
    isPlayer1Turn: bool

    @classmethod
    def from_match_info_dto(cls, match_info_dto):
        return PartialMatchInfoDto(
            match_info_dto.id,
            match_info_dto.roomId,
            match_info_dto.boardArray,
            match_info_dto.currentTurn,
            match_info_dto.isPlayer1Turn,
        )
