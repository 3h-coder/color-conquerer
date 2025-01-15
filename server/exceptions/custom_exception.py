class CustomException(Exception):
    """
    Extends the native Exception class. Mother class of all of our custom exceptions.

    INFO : Custom exception's messages are meant to be shown to the client (user).
    """

    def __init__(
        self,
        message: str | None,
        code: int | None = None,
        socket_connection_killer: bool = False,
    ):
        self.message = message

        if code is None:
            self.code = 500
        else:
            self.code = code

        self.socket_connection_killer = socket_connection_killer
        super().__init__(self.message)
