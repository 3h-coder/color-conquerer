from dataclasses import dataclass

from dto.cell_info_dto import CellDto
from dto.partial_match_info_dto import PartialMatchInfoDto
from dto.server_only.player_game_info_dto import PlayerGameInfoDto
from dto.player_info_bundle_dto import PlayerGameInfoBundleDto
from dto.server_only.player_info_dto import PlayerInfoDto
from dto.server_only.room_dto import RoomDto


@dataclass
class MatchInfoDto(PartialMatchInfoDto):
    """
    Stores both players' information on top of all the match information defined in :class:`PartialMatchInfoDto`
    """

    player1: PlayerInfoDto
    player2: PlayerInfoDto

    def get_player_game_info(self, player1: bool):
        return self.player1.playerGameInfo if player1 else self.player2.playerGameInfo

    def get_player_info_bundle(self):
        return PlayerGameInfoBundleDto(
            self.player1.playerGameInfo, self.player2.playerGameInfo
        )

    @staticmethod
    def get_initial_match_info(
        id: str, room_dto: RoomDto, initial_board_array: list[list[CellDto]]
    ):
        player1GameInfo = PlayerGameInfoDto.get_initial_player_game_info(
            is_player_1=True
        )

        player2GameInfo = PlayerGameInfoDto.get_initial_player_game_info(
            is_player_1=False
        )

        playerGameInfoBundle = PlayerGameInfoBundleDto(player1GameInfo, player2GameInfo)

        return MatchInfoDto(
            id=id,
            roomId=room_dto.id,
            boardArray=initial_board_array,
            currentTurn=0,
            isPlayer1Turn=False,
            playerInfoBundle=playerGameInfoBundle,
            player1=PlayerInfoDto.get_initial_player_info(
                room_dto.player1.user, room_dto.player1.playerId, True
            ),
            player2=PlayerInfoDto.get_initial_player_info(
                room_dto.player2.user, room_dto.player2.playerId, False
            ),
        )

    def both_players_are_dead(self):
        return self.player1_is_dead() and self.player2_is_dead()

    def player1_is_dead(self):
        return self._player_is_dead(True)

    def player2_is_dead(self):
        return self._player_is_dead(False)

    def _player_is_dead(self, player1: bool):
        return self.get_player_game_info(player1).player_is_dead()
