from flask import session

from config.config import logger
from handlers import room_handler
from session_variables import ROOM_ID, SOCKET_CONNECTED


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
        delete_open_room(room_id)
        return

    # if match started aka the room is closed, wait a bit then notify the room that the opponent left and close the match
    # wait a bit asynchronously (30 seconds ?)
    # emit to room opponent left/match ending, etc.


def delete_open_room(room_id: str):
    room_handler.remove_room(room_id)
    del session[ROOM_ID]
