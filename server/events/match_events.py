from flask import session
from flask_socketio import emit

from config.config import logger
from events.events import Events
from handlers import match_handler, room_handler
from session_variables import PLAYER_INFO, ROOM_ID


def handle_client_ready():
    """
    Marks the given player (i.e. the client sending emitting the event)
    as ready, possibly  starting the match if everyone is.
    """
    player_id = session.get(PLAYER_INFO).playerId
    room_id = session.get(ROOM_ID)

    mhu = match_handler.get_unit(room_id)
    mhu.players_ready[player_id] = True

    if all(value is True for value in mhu.players_ready.values()):
        logger.info(f"All players ready in the room {room_id}")
        mhu.start_match()
