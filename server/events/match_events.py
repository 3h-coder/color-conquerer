from flask import session
from flask_socketio import emit

from config.config import logger
from events.events import Events
from exceptions.match_info_error import MatchInfoError
from handlers import match_handler, room_handler


def handle_match_info_request():
    """
    Handles match info requests.

    Sends to the client the match info, creating the match along the way if necessary.
    Typically used for the client enters the play page or refreshes it.
    """
    try:

        room_id = session["room_id"]

        match_info = match_handler.get_match_info(room_id)

        emit(
            Events.SERVER_MATCH_INFO.value,
            match_info.to_json(),
            to=room_id,
            broadcast=True,
        )

    except Exception as ex:
        logger.error(f"An error occured while retrieving match info : {ex}")
        raise MatchInfoError(f"An error occured while retrieving match info : {ex}")
