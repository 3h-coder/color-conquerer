import pytest

from server import Server
from tests.utilities import mock_app, mock_queue_player_dto, mock_server


@pytest.fixture
def server():
    """Fixture to provide a new mock server instance"""
    return mock_server(mock_app())


@pytest.fixture
def server_test_client():
    app = mock_app()
    server = Server(app)
    return server.socketio.test_client(app=app.test_client())


@pytest.fixture
def queue_player_dto():
    """Fixture to provide a new mock QueuePlayerDto instance"""
    return mock_queue_player_dto()
