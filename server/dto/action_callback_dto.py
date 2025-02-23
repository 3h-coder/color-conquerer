from dataclasses import dataclass

from dto.base_dto import BaseDto
from dto.cell_dto import CellDto
from dto.match_action_dto import MatchActionDto


@dataclass
class ActionCallbackDto(BaseDto):
    id: int
    parentAction: MatchActionDto
    updatedGameBoard: list[list[CellDto]]
