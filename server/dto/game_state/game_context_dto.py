from dataclasses import dataclass
from typing import TYPE_CHECKING

from dto.base_dto import BaseDto
from dto.cell.cell_dto import CellDto
from dto.player.player_resources_bundle_dto import PlayerResourceBundleDto
from dto.spell.spells_dto import SpellsDto

if TYPE_CHECKING:
    from game_engine.models.actions.abstract.action_callback import ActionCallback
    from game_engine.models.match.match_context import MatchContext


@dataclass
class GameContextDto(BaseDto):
    gameBoard: list[list[CellDto]]
    playerResourceBundle: PlayerResourceBundleDto
    spellsDto: SpellsDto

    @staticmethod
    def from_match_context(match_context: "MatchContext", for_player1: bool):
        return GameContextDto(
            gameBoard=match_context.game_board.to_dto(for_player1),
            playerResourceBundle=PlayerResourceBundleDto.from_match_context(
                match_context
            ),
            spellsDto=match_context.get_spells_dto(for_player1),
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
            spellsDto=(
                player1_resources.get_spells_dto()
                if for_player1
                else player2_resources.get_spells_dto()
            ),
        )
