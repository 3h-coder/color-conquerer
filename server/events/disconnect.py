from flask import request, session
from flask_socketio import leave_room

from config.logger import logger
from constants.session_variables import PLAYER_INFO, ROOM_ID, SOCKET_CONNECTED
from dto.player_info_dto import PlayerInfoDto
from events.events import Events
from handlers import connection_handler, match_handler, room_handler
from handlers.match_handler_unit import MatchHandlerUnit
from utils import session_utils


def handle_disconnection():
    """
    Performs all the necessary actions when a socket disconnection occurs.

    For example, if the user is waiting for a match, then cancel the match request and destroy the room.

    Does nothing if there still is at least one socket connection.
    """
    connection_handler.register_disconnection(request.remote_addr)
    if not connection_handler.no_connection():
        return

    session[SOCKET_CONNECTED] = False

    room_id = session.get(ROOM_ID)
    if not room_id:
        return

    if room_handler.open_rooms.get(room_id):
        _handle_disconnection_in_queue(room_id)
        return

    player_info: PlayerInfoDto = session.get(PLAYER_INFO)
    if not player_info:
        return

    player_id = player_info.playerId
    mhu = match_handler.get_unit(room_id)

    # If the match is on going, wait a period of time before considering the player gone
    if mhu is not None and mhu.is_ongoing():
        _handle_disconnection_in_match(mhu, player_id)


def _handle_disconnection_in_queue(room_id):
    logger.debug("Disconnected while being in queue")
    room_handler.remove_open_room(room_id)
    leave_room(room_id)
    session_utils.clear_match_info()


def _handle_disconnection_in_match(mhu: MatchHandlerUnit, player_id):
    mhu.watch_player_exit(player_id, Events.SERVER_MATCH_END.value)
