from dataclasses import dataclass

from dto.base_dto import BaseDto
from dto.misc.cell_dto import CellDto


@dataclass
class PossibleActionsDto(BaseDto):
    """
    Meant to be sent to the client.
    """

    playerMode: int
    transientBoardArray: list[list[CellDto]]
