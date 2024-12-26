from dataclasses import dataclass

from constants.match_constants import MAX_HP_VALUE, MAX_MP_VALUE
from dto.partial_player_game_info_dto import PartialPlayerGameInfoDto


@dataclass
class PlayerGameInfoDto(PartialPlayerGameInfoDto):
    """
    Used to display the player's game information/characteristics
    such as their HP, MP and abilities.
    """

    # TODO : add stuff here

    @staticmethod
    def get_initial_player_game_info(is_player_1: bool):
        return PlayerGameInfoDto(
            player1=is_player_1,
            maxHP=MAX_HP_VALUE,
            currentHP=MAX_HP_VALUE,
            maxMP=MAX_MP_VALUE,
            currentMP=1 if is_player_1 else 0,
        )
