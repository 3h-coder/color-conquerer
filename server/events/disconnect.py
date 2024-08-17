import asyncio

from flask import session
from flask_socketio import emit, leave_room

from config.config import logger
from constants.session_variables import PLAYER_INFO, ROOM_ID, SOCKET_CONNECTED
from events.events import Events
from handlers import match_handler, room_handler


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

    # equivalent to in match being false or none
    if room_handler.open_rooms.get(room_id):
        logger.debug("Disconnected while being in queue")
        room_handler.remove_open_room(room_id)
        leave_room(room_id)
        clear_session()
        return

    mhu = match_handler.get_unit(room_id)

    # If the match is on going, wait a period of time before considering the player gone
    if mhu.is_ongoing():
        logger.debug("Disconnected while being in a match")
        match_handler_unit = match_handler.get_unit(room_id)
        match_handler_unit.start_exit_watcher(
            session.get(PLAYER_INFO), propagate_player_exit
        )


def propagate_player_exit():
    """
    Notifies the other player that their opponent has left, while clearing
    session data for the leaving user.
    """
    logger.debug("Propagating player exit")
    room_id = session.get(ROOM_ID)
    leave_room(room_id)
    clear_session()
    emit(Events.SERVER_MATCH_OPPONENT_LEFT.value, to=room_id)


def clear_session():
    del session[ROOM_ID]
    del session[PLAYER_INFO]
