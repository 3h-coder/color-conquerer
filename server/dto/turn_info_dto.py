from dataclasses import dataclass

from dto.base_dto import BaseDto


@dataclass
class TurnInfoDto(BaseDto):
    isPlayer1Turn: bool
    durationInS: int
