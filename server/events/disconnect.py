from flask import copy_current_request_context, session
from flask_socketio import emit, leave_room

from config.logger import logger
from constants.session_variables import PLAYER_INFO, ROOM_ID, SOCKET_CONNECTED
from events.events import Events
from handlers import match_handler, room_handler
from handlers.match_handler_unit import MatchHandlerUnit


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

    player_id = session.get(PLAYER_INFO).playerId

    if room_handler.open_rooms.get(room_id):
        _handle_disconnection_in_queue(room_id, player_id)

    mhu = match_handler.get_unit(room_id)

    # If the match is on going, wait a period of time before considering the player gone
    if mhu.is_ongoing():
        _handle_disconnection_in_match(mhu, player_id)


def _handle_disconnection_in_queue(room_id):
    logger.debug("Disconnected while being in queue")
    room_handler.remove_open_room(room_id)
    leave_room(room_id)
    _clear_session()
    return


def _handle_disconnection_in_match(mhu: MatchHandlerUnit, player_id):
    @copy_current_request_context
    def emit_player_exit(mhu: MatchHandlerUnit):

        emit(
            Events.SERVER_MATCH_END.value,
            mhu.match_closure_info.to_dict(),
            to=mhu.match_info.roomId,
        )

    mhu.watch_player_exit(player_id, emit_player_exit, (mhu,))


def _clear_session():
    del session[ROOM_ID]
    del session[PLAYER_INFO]
