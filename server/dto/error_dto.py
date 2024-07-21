from dataclasses import dataclass

from dto.base_dto import BaseDto
from exceptions.custom_exception import CustomException


@dataclass
class ErrorDto(BaseDto):
    error: str
    displayToUser: bool

    @classmethod
    def from_exception(cls, ex: Exception):
        dict_repr = {"error": str(ex)}
        dict_repr["displayToUser"] = isinstance(ex, CustomException)
        return dict_repr
