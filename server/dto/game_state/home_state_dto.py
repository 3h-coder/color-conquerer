from dataclasses import dataclass
from enum import IntEnum

from dto.base_dto import BaseDto


class HomeState(IntEnum):
    PLAY = 1
    JOIN_BACK = 2


@dataclass
class HomeStateDto(BaseDto):
    state: int  # HomeState.value
    topMessage: str
