from flask import session
from flask_socketio import leave_room

from config.config import logger
from handlers import match_handler, room_handler
from session_variables import IN_MATCH, PLAYER_INFO, ROOM_ID, SOCKET_CONNECTED


def handle_disconnection():
    """
    Performs all the necessary actions when a disconnection occurs.

    For example, if the user is waiting for a match, then cancel the match request and destroy the room.
    """
    session[SOCKET_CONNECTED] = False
    logger.debug("----- Socket disconnection -----")

    room_id = session.get(ROOM_ID)
    if not room_id:
        return

    if room_handler.open_rooms.get(room_id):
        room_handler.remove_room(room_id)
        leave_room(room_id)
        clear_session()
        return

    # if match started aka the room is closed, wait a bit then notify the room that the opponent left and close the match
    # wait a bit asynchronously (30 seconds ?)
    # emit to room opponent left/match ending, etc.
    if session.get(IN_MATCH) is True:
        match_handler_unit = match_handler.get_unit(room_id)
        match_handler_unit.start_exit_watcher(session.get(PLAYER_INFO))
        match_handler_unit.exit_watcher.add_done_callback()


def clear_session():
    del session[ROOM_ID]
    del session[PLAYER_INFO]
    del session[IN_MATCH]
