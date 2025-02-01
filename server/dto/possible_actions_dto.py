from dataclasses import dataclass

from dto.base_dto import BaseDto
from dto.cell_info_dto import CellDto
from dto.partial_match_action_dto import PartialMatchActionDto


@dataclass
class PossibleActionsDto(BaseDto):
    """
    Meant to be sent to the client.
    """

    playerMode: int
    transientBoardArray: list[list[CellDto]]
