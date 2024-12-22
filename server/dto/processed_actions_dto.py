from dataclasses import dataclass

from dto.base_dto import BaseDto
from dto.match_action_dto import MatchActionDto
from dto.partial_cell_info_dto import PartialCellInfoDto


@dataclass
class ProcessedActionsDto(BaseDto):
    processedActions: list[MatchActionDto]
    updatedBoardArray: list[list[PartialCellInfoDto]]
