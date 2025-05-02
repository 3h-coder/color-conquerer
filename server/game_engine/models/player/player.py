from dataclasses import dataclass

from dto.player.player_dto import PlayerDto
from game_engine.models.player.player_match_data import PlayerMatchData
from game_engine.models.player.player_resources import PlayerResources


@dataclass
class Player:
    """
    Stores all information relative to a player in a match,
    including the underlying user as well as their game match information.
    """

    player_id: str
    individual_room_id: str
    # Irrelevant for now, but just in case account registration gets implemented
    user_id: str
    is_player_1: bool
    resources: PlayerResources
    match_data: PlayerMatchData

    def to_dto(self):
        return PlayerDto(playerId=self.player_id, isPlayer1=self.is_player_1)

    @staticmethod
    def get_initial(
        player_id: str, individual_room_id: str, user_id: str, is_player_1: bool
    ):
        return Player(
            player_id=player_id,
            individual_room_id=individual_room_id,
            user_id=user_id,
            is_player_1=is_player_1,
            resources=PlayerResources.get_initial(),
            match_data=PlayerMatchData.get_initial(),
        )
