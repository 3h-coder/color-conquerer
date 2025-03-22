from dataclasses import dataclass
from typing import Any

from dto.base_dto import BaseDto
from dto.misc.cell_dto import CellDto


@dataclass
class PossibleActionsDto(BaseDto):
    playerMode: int
    transientBoardArray: list[list[CellDto]]
    additionalData: Any
