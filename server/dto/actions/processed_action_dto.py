from dataclasses import dataclass

from dto.actions.match_action_dto import MatchActionDto
from dto.base_dto import BaseDto
from dto.cell.cell_dto import CellDto
from dto.game_state.game_context_dto import GameContextDto


@dataclass
class ProcessedActionDto(BaseDto):
    processedAction: MatchActionDto
    playerMode: int
    updatedGameContext: GameContextDto
    # If the server mode is set to SHOW_PROCESSED_AND_POSSIBLE_ACTIONS, this board
    # will override the one from the turn info dto client side
    overridingTransientBoard: list[list[CellDto]] | None
