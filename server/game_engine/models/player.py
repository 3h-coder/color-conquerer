from dataclasses import dataclass

from game_engine.models.player_resources import PlayerResources


@dataclass
class Player:
    player_id: str
    # Irrelevant for now, but just in case account registration gets implemented
    user_id: str
    is_player_1: bool
    resources: PlayerResources
