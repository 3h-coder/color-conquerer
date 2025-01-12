import pytest

from unittest.mock import MagicMock
from flask import session

from constants.session_variables import ROOM_ID, SESSION_ID
from events.events import Events
from exceptions.queue_error import QueueError
from handlers import room_handler
from tests.utilities import mock_app, mock_queue_player_dto, mock_server


def test_registration_not_allowed_on_capacity():
    """
    Tests the room_handler.at_capacity() method, which should
    prevent queueing if it returns True.
    """

    server = mock_server(mock_app())
    event_listener = server.event_listeners[Events.CLIENT_QUEUE_REGISTER]
    with server.app.test_request_context():
        session[SESSION_ID] = "random_session_id"
        session[ROOM_ID] = "random_room_id"

        queue_player_dto = mock_queue_player_dto()

        room_handler.at_capacity = MagicMock(return_value=True)

        with pytest.raises(QueueError):
            event_listener(queue_player_dto)
