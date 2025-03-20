from dataclasses import dataclass

from dto.base_dto import BaseDto


@dataclass
class BooleanDto(BaseDto):
    value: bool
