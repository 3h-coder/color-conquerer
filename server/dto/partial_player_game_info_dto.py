from dataclasses import dataclass
from typing import TYPE_CHECKING

from dto.base_dto import BaseDto

if TYPE_CHECKING:
    from dto.player_game_info_dto import PlayerGameInfoDto


@dataclass
class PartialPlayerGameInfoDto(BaseDto):
    """
    Used to retrieve the stricly necessary info for the client
    to display about the player's opponent
    """

    player1: bool
    maxHP: int
    currentHP: int
    maxMP: int
    currentMP: int

    @classmethod
    def from_player_game_info(cls, player_game_info: "PlayerGameInfoDto"):
        return PartialPlayerGameInfoDto(
            player_game_info.player1,
            player_game_info.maxHP,
            player_game_info.currentHP,
            player_game_info.maxMP,
            player_game_info.currentMP,
        )
