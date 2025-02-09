from dataclasses import dataclass

from dto.base_dto import BaseDto
from dto.cell_dto import CellDto
from dto.match_action_dto import MatchActionDto
from dto.turn_context_dto import TurnContextDto


@dataclass
class ProcessedActionDto(BaseDto):
    """
    Meant to be sent to the client.
    """

    processedAction: MatchActionDto
    playerMode: int
    updatedTurnInfo: TurnContextDto
    # If the server mode is set to SHOW_PROCESSED_AND_POSSIBLE_ACTIONS, this board
    # will override the one from the turn info dto client side
    overridingTransientBoard: list[list[CellDto]] | None
