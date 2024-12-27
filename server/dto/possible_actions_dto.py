from dataclasses import dataclass

from dto.base_dto import BaseDto
from dto.partial_cell_info_dto import PartialCellInfoDto
from dto.partial_match_action_dto import PartialMatchActionDto


@dataclass
class PossibleActionsDto(BaseDto):
    """
    Meant to be sent to the client.
    """

    possibleActions: list[PartialMatchActionDto]
    playerMode: int
    transientBoardArray: list[list[PartialCellInfoDto]]
