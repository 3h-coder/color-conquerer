from dataclasses import dataclass
from enum import Enum
from dto.base_dto import BaseDto


class HomeState(Enum):
    PLAY = 1
    JOIN_BACK = 2


@dataclass
class HomeStateDto(BaseDto):
    state: int  # HomeState.value
    topMessage: str
    clearMatchSession: bool
