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
        error = str(ex)
        display_to_user = False
        socket_connection_killer = False

        if isinstance(ex, CustomException):
            display_to_user = True
            socket_connection_killer = ex.socket_connection_killer

        return ErrorDto(error, display_to_user, socket_connection_killer)
