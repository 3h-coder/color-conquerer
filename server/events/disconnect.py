from flask import request, session
from flask_socketio import leave_room

from config.logging import get_configured_logger
from constants.session_variables import PLAYER_INFO, ROOM_ID, SOCKET_CONNECTED
from dto.server_only.player_info_dto import PlayerInfoDto
from handlers import connection_handler, match_handler
from handlers.room_handler import RoomHandler
from server_gate import get_room_handler
from utils import session_utils

_logger = get_configured_logger(__name__)


def handle_disconnection():
    """
    Performs all the necessary actions when a socket disconnection occurs.

    For example, if the user is waiting for a match, then cancel the match request and destroy the room.

    Does nothing if there still is at least one socket connection.
    """
    room_handler = get_room_handler()
    connection_handler.register_disconnection(request.remote_addr)
    if not connection_handler.no_connection():
        return

    session[SOCKET_CONNECTED] = False

    room_id = session.get(ROOM_ID)
    if not room_id:
        return

    # May occur when there is an error while launching the match and the room gets
    # cleared up
    if not room_handler.room_exists(room_id):
        session_utils.clear_match_info()
        return

    if room_handler.open_rooms.get(room_id):
        _handle_disconnection_in_queue(room_id, room_handler)
        return

    player_info: PlayerInfoDto = session.get(PLAYER_INFO)
    if not player_info:
        return

    player_id = player_info.playerId
    match = match_handler.get_unit(room_id)

    # If the match is on going, wait a period of time before considering the player gone
    if match is not None and match.is_ongoing():
        match.watch_player_exit(player_id)


def _handle_disconnection_in_queue(room_id, room_handler: RoomHandler):
    """Removes the room and clears the user's session information relative to match information"""

    _logger.debug(f"({request.remote_addr}) | Disconnected while being in queue")

    room_handler.remove_open_room(room_id)
    leave_room(room_id)
    session_utils.clear_match_info()
