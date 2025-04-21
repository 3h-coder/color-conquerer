import pytest

from tests.helpers.match_helper import MatchHelper
from tests.utilities.mocks import mock_queue_player_dto, mock_server


@pytest.fixture
def match():
    """Fixture to provide a match helper instance"""
    return MatchHelper()


@pytest.fixture
def started_match():
    """Fixture to provide a started match helper instance"""
    match = MatchHelper()
    match.start()
    return match


@pytest.fixture
def server():
    """Fixture to provide a new mock server instance"""
    return mock_server()


@pytest.fixture
def queue_player_dto():
    """Fixture to provide a new mock QueuePlayerDto instance"""
    return mock_queue_player_dto()
