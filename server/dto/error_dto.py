from dataclasses import dataclass

from dto.base_dto import BaseDto


@dataclass
class ErrorDto(BaseDto):
    error: str

    @classmethod
    def from_exception(ex: Exception):
        return ErrorDto(error=str(ex))
