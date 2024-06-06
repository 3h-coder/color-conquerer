class CustomException(Exception):
    """Extends the native Exception class. Mother class of all of our custom exceptions."""

    def __init__(self, message: str | None, code: int | None = None):
        self.message = message

        if code is None:
            self.code = 500
        else:
            self.code = code
        super().__init__(self.message)
