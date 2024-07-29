import asyncio
from flask import session
from flask_socketio import emit, leave_room
from events.events import Events

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

    # equivalent to in match being false or none
    if room_handler.open_rooms.get(room_id):
        room_handler.remove_room(room_id)
        leave_room(room_id)
        clear_session()
        return
    
    in_match = session.get(IN_MATCH)
    if not in_match:
        logger.warning(f"Inconsistent data : The user is not in an open room yet the {IN_MATCH} "
                       f"session variable was {in_match}")

    # if match started aka the room is closed, wait a bit then notify the room that the opponent left and close the match
    # wait a bit asynchronously (30 seconds ?)
    # emit to room opponent left/match ending, etc.
    if in_match is True:
        match_handler_unit = match_handler.get_unit(room_id)
        match_handler_unit.start_exit_watcher(session.get(PLAYER_INFO))
        match_handler_unit.exit_watcher.add_done_callback(propagate_player_exit)


def clear_session():
    del session[ROOM_ID]
    del session[PLAYER_INFO]
    del session[IN_MATCH]

def propagate_player_exit(task: asyncio.Task[bool], room_id: str):
    """
    Notifies the other player that their opponent has left, while clearing
    session data for the leaving user.
    """
    
    if task.cancelled():
        logger.debug("The player exit was cancelled, not propagating")
    elif ex := task.exception() is not None:
        logger.error(f"An error occured while trying to confirm the player exit : {str(ex)}")
    else:
        logger.debug("Propagating player exit")
        leave_room(room_id)
        clear_session()
        emit(Events.SERVER_MATCH_OPPONENT_LEFT.value, to=room_id)
