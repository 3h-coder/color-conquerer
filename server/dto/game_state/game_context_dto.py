from dataclasses import dataclass
from typing import TYPE_CHECKING

from dto.base_dto import BaseDto
from dto.misc.cell_dto import CellDto
from dto.player.player_resources_bundle_dto import PlayerResourceBundleDto

if TYPE_CHECKING:
    from game_engine.models.actions.callbacks.action_callback import ActionCallback
    from game_engine.models.match_context import MatchContext
    from game_engine.models.dtos.turn_context import TurnContext


@dataclass
class GameContextDto(BaseDto):
    gameBoard: list[list[CellDto]]
    playerResourceBundle: PlayerResourceBundleDto

    @staticmethod
    def from_match_context(match_context: "MatchContext", for_player1: bool):
        return GameContextDto(
            gameBoard=match_context.game_board.to_dto(for_player1),
            playerResourceBundle=PlayerResourceBundleDto.from_match_context(
                match_context
            ),
        )

    @staticmethod
    def from_turn_context(turn_context: "TurnContext", for_player1: bool):
        return GameContextDto(
            gameBoard=turn_context.updated_board.to_dto(for_player1),
            playerResourceBundle=PlayerResourceBundleDto.from_turn_state(
                turn_context.current_state
            ),
        )

    @staticmethod
    def from_action_callback(callback: "ActionCallback", for_player1: bool):
        player1_resources, player2_resources = callback.updated_player_resources
        return GameContextDto(
            gameBoard=callback.updated_game_board.to_dto(for_player1),
            playerResourceBundle=PlayerResourceBundleDto(
                player1Resources=player1_resources.to_dto(),
                player2Resources=player2_resources.to_dto(),
            ),
        )
