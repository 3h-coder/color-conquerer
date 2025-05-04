from exceptions.custom_exception import CustomException


class MatchLaunchError(CustomException):

    def __init__(self, broadcast_to: str):
        message = "Failed to start the match"
        super().__init__(
            message=message, socket_connection_killer=True, broadcast_to=broadcast_to
        )
