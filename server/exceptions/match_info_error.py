from exceptions.custom_exception import CustomException


class MatchInfoError(CustomException):
    """
    Any exception that occurs when retrieving match info
    """

    def __init__(self, message: str | None = None):
        if not message:
            self.message = "An error occured during match info retrieval"
        else:
            self.message = message

        self.code = 500
        super().__init__(self.message, self.code)
