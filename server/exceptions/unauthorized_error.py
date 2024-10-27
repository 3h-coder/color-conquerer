from exceptions.custom_exception import CustomException


class UnauthorizedError(CustomException):
    def __init__(
        self, message: str | None = None, socket_connection_killer: bool = False
    ):
        if not message:
            message = "The requester is not authorized to perform the operation or access the resource"

        super().__init__(message, 401, socket_connection_killer)
