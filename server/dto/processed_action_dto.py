from dataclasses import dataclass

from dto.base_dto import BaseDto
from dto.partial_match_action_dto import PartialMatchActionDto
from dto.partial_match_info_dto import PartialMatchInfoDto


@dataclass
class ProcessedActionDto(BaseDto):
    """
    Meant to be sent to the client.
    """

    processedAction: PartialMatchActionDto
    playerMode: int
    updatedMatchInfo: PartialMatchInfoDto
