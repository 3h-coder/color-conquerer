from dataclasses import dataclass

from constants.match_constants import TURN_DURATION_IN_S
from dto.partial_match_info_dto import PartialMatchInfoDto
from dto.player_game_info_dto import PlayerGameInfoDto
from dto.server_only.player_info_dto import PlayerInfoDto
from dto.server_only.room_dto import RoomDto


@dataclass
class MatchInfoDto(PartialMatchInfoDto):
    player1: PlayerInfoDto
    player2: PlayerInfoDto

    @classmethod
    def get_initial_match_info(cls, id: str, room_dto: RoomDto, initial_board_array):
        return MatchInfoDto(
            id=id,
            roomId=room_dto.id,
            boardArray=initial_board_array,
            currentTurn=0,
            isPlayer1Turn=False,
            totalTurnDurationInS=TURN_DURATION_IN_S,
            player1=PlayerInfoDto(
                user=room_dto.player1.user,
                playerId=room_dto.player1.playerId,
                isPlayer1=True,
                playerGameInfo=PlayerGameInfoDto.get_initial_player_game_info(),
            ),
            player2=PlayerInfoDto(
                user=room_dto.player2.user,
                playerId=room_dto.player2.playerId,
                isPlayer1=False,
                playerGameInfo=PlayerGameInfoDto.get_initial_player_game_info(),
            ),
        )
