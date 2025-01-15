from unittest.mock import MagicMock

import pytest
from flask import session

from constants.session_variables import ROOM_ID, SESSION_ID
from dto.queue_player_dto import QueuePlayerDto
from events.events import Events
from exceptions.queue_error import QueueError
from server import Server


def test_registration_not_allowed_without_initialized_session(
    server: Server, queue_player_dto: QueuePlayerDto
):
    # Arrange
    event_listener = server.event_listeners[Events.CLIENT_QUEUE_REGISTER]

    with server.app.test_request_context():
        session[SESSION_ID] = None

        # Act & Assert
        with pytest.raises(QueueError, match=QueueError.NO_SESSION_ERROR_MSG):
            event_listener(queue_player_dto.to_dict())


def test_registration_not_allowed_if_already_registered(
    server: Server, queue_player_dto: QueuePlayerDto
):
    # Arrange
    event_listener = server.event_listeners[Events.CLIENT_QUEUE_REGISTER]

    with server.app.test_request_context():
        session[SESSION_ID] = "random_session_id"
        session[ROOM_ID] = "random_room_id"

        # Act & Assert
        with pytest.raises(QueueError, match=QueueError.ALREADY_REGISTERED_ERROR_MSG):
            event_listener(queue_player_dto.to_dict())


def test_registration_not_allowed_at_capacity(
    server: Server, queue_player_dto: QueuePlayerDto
):
    """
    Tests the room_handler.at_capacity() method, which should
    prevent queueing if it returns True.
    """
    # Arrange
    event_listener = server.event_listeners[Events.CLIENT_QUEUE_REGISTER]
    room_handler = server.room_handler

    with server.app.test_request_context():
        session[SESSION_ID] = "random_session_id"

        room_handler.at_capacity = MagicMock(return_value=True)

        # Act & Assert
        with pytest.raises(QueueError, match=QueueError.MAX_CAPACITY_ERROR_MSG):
            event_listener(queue_player_dto.to_dict())

        room_handler.at_capacity.assert_called_once_with()


def test_successful_registration_puts_queuer_in_an_open_room(
    server: Server, queue_player_dto: QueuePlayerDto
):
    """
    Makes sure that the room_handler ends up with one open room where the
    queuer is.
    """
    # Arrange
    room_handler = server.room_handler
    flask_test_client = server.app.test_client()

    response = flask_test_client.get("/session")
    assert response.status_code == 200

    socketio_test_client = server.socketio.test_client(
        server.app, flask_test_client=flask_test_client
    )

    # Act
    socketio_test_client.emit(Events.CLIENT_QUEUE_REGISTER, queue_player_dto.to_dict())

    # Assert
    assert len(room_handler.closed_rooms) == 0
    assert len(room_handler.open_rooms) == 1

    open_room_dto = next(iter(room_handler.open_rooms.values()))
    assert queue_player_dto.user == open_room_dto.player1.user
