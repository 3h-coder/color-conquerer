from flask import request, session
from flask_socketio import leave_room

from config.logging import get_configured_logger
from handlers.room_handler import RoomHandler
from server_gate import get_connection_handler, get_match_handler, get_room_handler
from session_management import session_utils
from session_management.models.session_player import SessionPlayer
from session_management.session_variables import PLAYER_INFO, ROOM_ID, SOCKET_CONNECTED
from utils import logging_utils

_logger = get_configured_logger(
    __name__, prefix_getter=lambda: logging_utils.flask_request_remote_addr_prefix()
)


def handle_disconnection():
    """
    Performs all the necessary actions when a socket disconnection occurs.

    For example, if the user is waiting for a match, then cancel the match request and destroy the room.

    Does nothing if there still is at least one socket connection.
    """
    connection_handler = get_connection_handler()
    room_handler = get_room_handler()

    connection_handler.register_disconnection(request.remote_addr)
    if not connection_handler.no_connection():
        return

    session[SOCKET_CONNECTED] = False

    room_id = session.get(ROOM_ID)
    if not room_id:
        return

    # May occur when there is an error while launching the match
    # before the room could be placed in the closed rooms
    if not room_handler.room_exists(room_id):
        _leave_socket_room_and_clear_session(room_id)
        return

    if room_handler.open_rooms.get(room_id):
        _handle_disconnection_in_queue(room_id, room_handler)
        return

    player_info: SessionPlayer = session.get(PLAYER_INFO)
    if not player_info:
        return

    match_handler = get_match_handler()

    player_id = player_info.player_id
    match = match_handler.get_unit(room_id)

    # May happen if the match creation failed
    if match is None:
        _handle_disconnection_with_room_id_but_no_match(room_id)

    elif match.is_ongoing():
        match.watch_player_exit(player_id)
        match.set_player_as_idle(player_id)

    elif match.is_cancelled():
        _handle_disconnection_in_cancelled_match(room_id)

    elif match.is_ended():
        _handle_disconnection_in_ended_match(room_id)


def _handle_disconnection_in_queue(room_id: str, room_handler: RoomHandler):
    """Removes the room, leaves the socket room and clears the user's session information relative to match information"""

    _logger.debug(f"Disconnected while being in queue")
    room_handler.remove_open_room(room_id)
    _leave_socket_room_and_clear_session(room_id)


def _handle_disconnection_with_room_id_but_no_match(room_id: str):
    """Clears the user's session information relative to match information"""

    _logger.debug(f"Disconnected with a set ROOM_ID but no match")
    _leave_socket_room_and_clear_session(room_id)


def _handle_disconnection_in_cancelled_match(room_id: str):
    """Leaves the socket room and clears the user's session information relative to match information"""

    _logger.debug(f"Disconnected after match cancellation")
    _leave_socket_room_and_clear_session(room_id)


def _handle_disconnection_in_ended_match(room_id: str):
    """Leaves the socket room and clears the user's session information relative to match information"""

    _logger.debug(f"Disconnected after match ending")
    _leave_socket_room_and_clear_session(room_id)


def _leave_socket_room_and_clear_session(room_id: str):
    leave_room(room_id)
    session_utils.clear_match_info()
