from dataclasses import dataclass

from dto.base_dto import BaseDto
from dto.partial_cell_info_dto import PartialCellInfoDto
from dto.partial_match_action_dto import PartialMatchActionDto


@dataclass
class ProcessedActionsDto(BaseDto):
    """
    Meant to be sent to the client.
    """

    processedActions: list[PartialMatchActionDto]
    updatedBoardArray: list[list[PartialCellInfoDto]]
