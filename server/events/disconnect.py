from flask import session
from flask_socketio import emit

from events.events import Events


def handle_disconnection():
    # TODO:
    # if match not started destroy closed room
    # if match started, player who didn't leave automatically wins -> destroy closed room
    room_id = session.get("room_id")
    if not room_id:
        return

    if room_id:
        emit(Events.SERVER_MATCH_OPPONENT_LEFT.value, to=room_id, broadcast=True)
