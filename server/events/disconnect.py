from flask import session
from flask_socketio import emit, leave_room

from config.logger import logger
from constants.session_variables import PLAYER_INFO, ROOM_ID, SOCKET_CONNECTED
from dto.match_closure_dto import EndingReason
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


def _handle_disconnection_in_queue(room_id, player_id):
    logger.debug("Disconnected while being in queue")
    room_handler.remove_open_room(room_id)
    match_handler.remove_exit_watcher(player_id)
    leave_room(room_id)
    _clear_session()
    return


def _handle_disconnection_in_match(mhu: MatchHandlerUnit, player_id):
    logger.debug("Disconnected while being in a match, starting exit watcher")
    match_handler.start_exit_watcher(
        player_id,
        exit_function=_leave_match,
        exit_function_args=(mhu, player_id),
    )


def _leave_match(mhu: MatchHandlerUnit, player_id):
    from main import server

    mhu.end_match(EndingReason.PLAYER_LEFT.value, loser_id=player_id)
    server.socketio.emit(
        Events.SERVER_MATCH_END.value,
        mhu.match_closure_info.to_dict(),
        to=mhu.match_info.roomId,
    )


def _clear_session():
    del session[ROOM_ID]
    del session[PLAYER_INFO]
