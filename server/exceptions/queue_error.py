from exceptions.custom_exception import CustomException


class QueueError(CustomException):
    """
    Any exception that occurs during the queueing process
    """

    def __init__(self, message: str | None = None):
        if not message:
            self.message = "An error occured during queueing"
        else:
            self.message = message

        self.code = 500
        super().__init__(self.message, self.code)
