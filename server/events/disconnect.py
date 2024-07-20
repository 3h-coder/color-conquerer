from flask import session
from flask_socketio import emit

from config.config import logger
from events.events import Events


def handle_disconnection():
    # TODO:
    # if match not started destroy closed room
    # if match started, player who didn't leave automatically wins -> destroy closed room
    room_id = session.get("room_id")
    if not room_id:
        return

    session["connected"] = False
    logger.debug("Session disconnection")
    emit(Events.SERVER_MATCH_OPPONENT_LEFT.value, to=room_id, broadcast=True)
