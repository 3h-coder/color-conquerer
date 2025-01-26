from dataclasses import dataclass

from dto.partial_player_info_dto import PartialPlayerInfoDto
from dto.server_only.player_game_info_dto import PlayerGameInfoDto
from dto.user_dto import UserDto


@dataclass
class PlayerInfoDto(PartialPlayerInfoDto):
    """
    Stores all information relative to a player in a match,
    including the underlying user as well as their game match information.
    """

    user: UserDto
    playerGameInfo: PlayerGameInfoDto

    @staticmethod
    def get_initial_player_info(user: UserDto, player_id: str, is_player_1: bool):
        return PlayerInfoDto(
            user=user,
            playerId=player_id,
            isPlayer1=is_player_1,
            playerGameInfo=PlayerGameInfoDto.get_initial_player_game_info(
                is_player_1=is_player_1
            ),
        )
