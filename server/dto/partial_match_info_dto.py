from dataclasses import dataclass
from typing import TYPE_CHECKING

from dto.base_dto import BaseDto
from dto.cell_info_dto import CellInfoDto
from dto.partial_player_game_info_dto import PartialPlayerGameInfoDto

if TYPE_CHECKING:
    from dto.server_only.match_info_dto import MatchInfoDto


@dataclass
class PartialMatchInfoDto(BaseDto):
    """
    Stores the basic match info such as the match's id, the associated room id,
    the board array or the current turn.
    """

    id: str
    roomId: str
    boardArray: list[list[CellInfoDto]]
    currentTurn: int
    isPlayer1Turn: bool
    totalTurnDurationInS: int

    @classmethod
    def from_match_info_dto(cls, match_info_dto: "MatchInfoDto"):
        return PartialMatchInfoDto(
            match_info_dto.id,
            match_info_dto.roomId,
            match_info_dto.boardArray,
            match_info_dto.currentTurn,
            match_info_dto.isPlayer1Turn,
            match_info_dto.totalTurnDurationInS,
        )
