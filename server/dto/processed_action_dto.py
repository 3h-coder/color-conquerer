from dataclasses import dataclass

from dto.base_dto import BaseDto
from dto.partial_cell_info_dto import PartialCellInfoDto
from dto.partial_match_action_dto import PartialMatchActionDto
from dto.turn_info_dto import TurnInfoDto


@dataclass
class ProcessedActionDto(BaseDto):
    """
    Meant to be sent to the client.
    """

    processedAction: PartialMatchActionDto
    playerMode: int
    updatedTurnInfo: TurnInfoDto
    # If the server mode is set to SHOW_PROCESSED_AND_POSSIBLE_ACTIONS, this board
    # will override the one from the turn info dto client side
    overridingTransientBoard: list[list[PartialCellInfoDto]] | None
