from dataclasses import dataclass

from dto.base_dto import BaseDto


@dataclass
class MessageDto(BaseDto):
    message: str

    @staticmethod
    def from_string(string: str):
        return MessageDto(message=string)
