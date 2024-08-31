import uuid

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
        _handle_disconnection_in_match(mhu, room_id, player_id)


def _handle_disconnection_in_queue(room_id, player_id):
    logger.debug("Disconnected while being in queue")
    room_handler.remove_open_room(room_id)
    match_handler.remove_exit_watcher(player_id)
    leave_room(room_id)
    _clear_session()
    return


def _handle_disconnection_in_match(mhu: MatchHandlerUnit, room_id, player_id):
    from main import server

    logger.debug("Disconnected while being in a match, starting exit watcher")
    request_context = server.app.test_request_context()
    req_context_key = str(uuid.uuid4())
    server.save_request_context(req_context_key, request_context)

    match_handler.start_exit_watcher(
        player_id,
        exit_function=_leave_match,
        exit_function_args=(req_context_key, mhu, room_id),
    )


def _leave_match(req_context_key: str, mhu: MatchHandlerUnit, room_id):
    from main import server

    with server.app.app_context():
        with server.consume_request_context(req_context_key):
            mhu.end_match("Player left")
            _propagate_player_exit(room_id)


def _propagate_player_exit(room_id: str):
    """
    Notifies the other player that their opponent has left, while clearing
    session data for the leaving user.
    """
    logger.debug("Propagating player exit")
    leave_room(room_id)
    _clear_session()
    emit(Events.SERVER_MATCH_OPPONENT_LEFT.value, to=room_id)


def _clear_session():
    del session[ROOM_ID]
    del session[PLAYER_INFO]
