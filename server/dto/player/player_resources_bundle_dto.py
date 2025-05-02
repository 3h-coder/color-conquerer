from dataclasses import dataclass

from dto.player.player_resources_dto import PlayerResourcesDto
from game_engine.models.dtos.match_context import MatchContext
from game_engine.models.turn.turn_state import TurnState


@dataclass
class PlayerResourceBundleDto:
    player1Resources: PlayerResourcesDto
    player2Resources: PlayerResourcesDto

    @staticmethod
    def from_turn_state(turn_state: TurnState):
        return PlayerResourceBundleDto(
            player1Resources=turn_state.player1_resources.to_dto(),
            player2Resources=turn_state.player2_resources.to_dto(),
        )

    @staticmethod
    def from_match_context(match_context: MatchContext):
        return PlayerResourceBundleDto(
            player1Resources=match_context.player1.resources.to_dto(),
            player2Resources=match_context.player2.resources.to_dto(),
        )
