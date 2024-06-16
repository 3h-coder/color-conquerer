from exceptions.custom_exception import CustomException


class UnauthorizedError(CustomException):
    def __init__(self, message: str | None = None):
        if not message:
            self.message = "The requester is not allowed to perform the operation"
        else:
            self.message = message
        self.code = 401
        super().__init__(self.message, self.code)
