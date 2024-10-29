from exceptions.custom_exception import CustomException


class ServerError(CustomException):
    """
    Raise this exception when you want to let the user know about a specific server error in
    a socket context.
    """

    def __init__(
        self, message: str | None = None, socket_connection_killer: bool = False
    ):
        # Currently overriden client side if in a blueprint
        if not message:
            message = "An unexpected error has occured."

        super().__init__(message, 500, socket_connection_killer)
