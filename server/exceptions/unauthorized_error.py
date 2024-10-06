from exceptions.custom_exception import CustomException


class UnauthorizedError(CustomException):
    def __init__(self, message: str | None = None):
        if not message:
            message = "The requester is not allowed to perform the operation"

        super().__init__(message, 401)
