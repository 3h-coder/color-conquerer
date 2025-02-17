from dataclasses import dataclass

from dto.base_dto import BaseDto


@dataclass
class ActionCallbackDto(BaseDto):
    ID: int
