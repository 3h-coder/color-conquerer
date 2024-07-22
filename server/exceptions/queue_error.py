from exceptions.custom_exception import CustomException


class QueueError(CustomException):
    """
    Any exception that occurs during the queueing process
    """

    def __init__(
        self, message: str | None = None, socket_connection_killer: bool = False
    ):
        if not message:
            message = "An error occured during queueing"

        super().__init__(message, 500, socket_connection_killer)
