"""
Utility methods for test setup and execution.
"""

from application import Application
from dto.queue_player_dto import QueuePlayerDto
from dto.user_dto import UserDto
from server import Server


def mock_app():
    """
    Not an actual mock but a real Application instance initialized with
    minimal configuration strictly necessary for tests.
    """
    return Application(__name__, test_instance=True)


def mock_server(app: Application):
    """
    Not an actual mock but a real Server instance for testing purposes.
    """
    return Server(app)


def mock_user_dto(
    id: str = "mock_user_id",
    username: str = "mock user",
    is_authenticating=False,
    is_authenticated=False,
):
    return UserDto(id, username, is_authenticating, is_authenticated)


def mock_queue_player_dto(user: UserDto = None, playerId: str = "mock_player_id"):
    if user is None:
        user = mock_user_dto()
    return QueuePlayerDto(user, playerId)
