from exceptions.custom_exception import CustomException


class QueueError(CustomException):
    """
    Any exception that occurs during the queueing process
    """

    NO_SESSION_ERROR_MSG = "Something went wrong, please refresh the page and try again"
    ALREADY_REGISTERED_ERROR_MSG = "You are already registered in the queue"
    MAX_CAPACITY_ERROR_MSG = (
        "The server has reached its maximum capacity, please try again later"
    )

    def __init__(
        self, message: str | None = None, socket_connection_killer: bool = False
    ):
        if not message:
            message = "An error occured during queueing"

        super().__init__(message, 500, socket_connection_killer)
