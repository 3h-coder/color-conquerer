"""
Utility methods for test setup and execution.
"""

from flask.testing import FlaskClient
from application import Application
from dto.queue_player_dto import QueuePlayerDto
from dto.user_dto import UserDto
from server import Server

# region Mocks


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


# endregion


def initialize_session(flask_test_client: FlaskClient):
    response = flask_test_client.get("/session")
    assert response.status_code == 200
