from dataclasses import dataclass
from typing import TYPE_CHECKING

from dto.base_dto import BaseDto
from dto.spell_dto import SpellDto

if TYPE_CHECKING:
    from dto.server_only.player_game_info_dto import PlayerGameInfoDto


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
    # WARNING : player2 spells must not be sent to player1 and vice versa
    # in which case the list must be empty
    spells: list[SpellDto]

    @staticmethod
    def from_player_game_info(player_game_info: "PlayerGameInfoDto"):
        if player_game_info is None:
            return None

        return PartialPlayerGameInfoDto(
            player_game_info.player1,
            player_game_info.maxHP,
            player_game_info.currentHP,
            player_game_info.maxMP,
            player_game_info.currentMP,
            player_game_info.spells,
        )
