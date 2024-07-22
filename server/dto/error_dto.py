from dataclasses import dataclass

from dto.base_dto import BaseDto
from exceptions.custom_exception import CustomException


@dataclass
class ErrorDto(BaseDto):
    error: str
    displayToUser: bool
    socketConnectionKiller: bool

    @classmethod
    def from_exception(cls, ex: Exception):
        dict_repr = {"error": str(ex)}

        if isinstance(ex, CustomException):
            dict_repr["displayToUser"] = True
            dict_repr["socketConnectionKiller"] = ex.socket_connection_killer
        else:
            dict_repr["displayToUser"] = False
            dict_repr["socketConnectionKiller"] = False

        return dict_repr
