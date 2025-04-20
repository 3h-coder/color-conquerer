from unittest.mock import MagicMock

import pytest
from flask import session

from constants.session_variables import ROOM_ID, SESSION_ID
from dto.player.queue_player_dto import QueuePlayerDto
from events.events import Events
from exceptions.queue_error import QueueError
from server import Server
from tests.utilities.utilities import initialize_session


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

        room_handler.at_capacity.assert_called_once()


def test_successful_registration_puts_queuer_in_an_open_room(
    server: Server, queue_player_dto: QueuePlayerDto
):
    """
    Makes sure that the room_handler ends up with one open room where the
    queuer is.
    """
    # Arrange
    room_handler = server.room_handler
    client = server.app.test_client()

    initialize_session(client)

    socketio_test_client = server.socketio.test_client(
        server.app, flask_test_client=client
    )

    # Act
    socketio_test_client.emit(Events.CLIENT_QUEUE_REGISTER, queue_player_dto.to_dict())

    # Assert
    assert len(room_handler.closed_rooms) == 0
    assert len(room_handler.open_rooms) == 1

    open_room = next(iter(room_handler.open_rooms.values()))
    assert queue_player_dto.user == open_room.player1_queue_dto.user


def test_two_players_queueing_starts_a_match(
    server: Server, queue_player_dto: QueuePlayerDto
):
    """
    Makes sure that a match is launched when 2 players successfully
    register in the queue.
    """
    # Arrange
    room_handler = server.room_handler
    match_handler = server.match_handler

    client1 = server.app.test_client()
    client2 = server.app.test_client()

    initialize_session(client1)
    initialize_session(client2)

    socketio_client1 = server.socketio.test_client(
        server.app, flask_test_client=client1
    )
    socketio_client2 = server.socketio.test_client(
        server.app, flask_test_client=client2
    )

    # Act
    socketio_client1.emit(Events.CLIENT_QUEUE_REGISTER, queue_player_dto.to_dict())
    socketio_client2.emit(Events.CLIENT_QUEUE_REGISTER, queue_player_dto.to_dict())

    # Assert
    assert len(room_handler.open_rooms) == 0
    assert len(room_handler.closed_rooms) == 1
    assert len(match_handler.units) == 1

    closed_room = next(iter(room_handler.closed_rooms.values()))
    match = match_handler.get_unit(closed_room.id)

    assert match is not None
    assert match.is_waiting_to_start()
