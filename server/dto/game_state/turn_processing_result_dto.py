from dataclasses import dataclass

from dto.base_dto import BaseDto


@dataclass
class TurnProcessingResultDto(BaseDto):
    fatigueDamage: int
