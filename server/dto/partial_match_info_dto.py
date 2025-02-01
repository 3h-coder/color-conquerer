from dataclasses import dataclass
from typing import TYPE_CHECKING

from dto.base_dto import BaseDto
from dto.cell_dto import CellDto
from dto.player_info_bundle_dto import PlayerGameInfoBundleDto
from utils.board_utils import to_client_board_dto

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
    boardArray: list[list[CellDto]]
    currentTurn: int
    isPlayer1Turn: bool
    # This property is currently not updated server side,
    # but is recalculated when sent to the client via
    # the from_match_info_dto method below.
    playerInfoBundle: PlayerGameInfoBundleDto

    @staticmethod
    def from_match_info_dto(match_info_dto: "MatchInfoDto"):
        return PartialMatchInfoDto(
            match_info_dto.id,
            match_info_dto.roomId,
            to_client_board_dto(match_info_dto.boardArray),
            match_info_dto.currentTurn,
            match_info_dto.isPlayer1Turn,
            match_info_dto.get_player_info_bundle(),
        )
