from enum import StrEnum


class EndingReason(StrEnum):
    PLAYER_VICTORY = "player victory"
    DRAW = "draw"
    PLAYER_CONCEDED = "player conceded"
    PLAYER_LEFT = "player left"
    PLAYER_INACTIVE = "player inactive"
    # When the player dies from damage due to low stamina
    FATIGUE = "fatigue"
