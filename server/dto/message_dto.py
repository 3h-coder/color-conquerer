from dataclasses import dataclass

from dto.base_dto import BaseDto


class MessageDto(BaseDto):
    message: str

    @classmethod
    def from_string(cls, string: str):
        return MessageDto(message=string)
