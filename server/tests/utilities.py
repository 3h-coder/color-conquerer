"""
Utility methods for test setup and execution.
"""

from application import Application
from dto.queue_player_dto import QueuePlayerDto
from dto.user_dto import UserDto
from server import Server


def mock_app():
    return Application(__name__, test_instance=True)


def mock_server(app: Application):
    return Server(app)


def mock_user_dto(id: str = "mock_user_id", username: str = "mock user"):
    return UserDto(id, username)


def mock_queue_player_dto(user: UserDto = None, playerId: str = "mock_player_id"):
    if user is None:
        user = mock_user_dto()
    return QueuePlayerDto(user, playerId)
