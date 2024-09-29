from exceptions.custom_exception import CustomException

class WrongDataError(CustomException):
    """
    Raise this exception when the client is sending incorrect or unknown data.
    """
    def __init__(self, message: str | None = None, socket_connection_killer: bool = False, code: int = 400):
        if not message:
            message = "The data is either malformed or could not be resolved"

        super().__init__(message, code, socket_connection_killer)