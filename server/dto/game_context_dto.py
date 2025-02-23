from dataclasses import dataclass
from typing import TYPE_CHECKING

from dto.base_dto import BaseDto
from dto.cell_dto import CellDto
from dto.player_resources_bundle_dto import PlayerResourceBundleDto

if TYPE_CHECKING:
    from game_engine.models.match_context import MatchContext
    from game_engine.models.turn_context import TurnContext


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

    def from_turn_context(turn_context: "TurnContext", for_player1: bool):
        return GameContextDto(
            gameBoard=turn_context.updated_board.to_dto(for_player1),
            playerResourceBundle=PlayerResourceBundleDto.from_turn_state(
                turn_context.current_state
            ),
        )
