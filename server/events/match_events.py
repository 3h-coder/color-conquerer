import logging

from flask import session
from flask_socketio import emit, join_room

from config.logging import with_logger_configuration
from constants.session_variables import PLAYER_INFO, ROOM_ID
from dto.message_dto import MessageDto
from events.events import Events
from handlers import match_handler
from utils import session_utils

_logger: logging.Logger = None


@with_logger_configuration(_logger, __name__)
def handle_client_ready():
    """
    Marks the given player (i.e. the client sending emitting the event)
    as ready, possibly  starting the match if everyone is.
    """
    player_id = session.get(PLAYER_INFO).playerId
    room_id = session.get(ROOM_ID)

    join_room(room_id)

    mhu = match_handler.get_unit(room_id)
    mhu.players_ready[player_id] = True

    # The start match event is what the client uses to render the game
    if mhu.is_ongoing():
        emit(Events.SERVER_MATCH_STARTED.value)
    elif mhu.is_waiting_to_start():
        if all(value is True for value in mhu.players_ready.values()):
            _logger.info(f"All players ready in the room {room_id}")
            mhu.start_match(Events.SERVER_TURN_SWAP.value)
            emit(Events.SERVER_MATCH_STARTED.value, to=room_id, broadcast=True)
        else:
            emit(
                Events.SERVER_SET_WAITING_TEXT.value,
                MessageDto.from_string("Waiting for your opponent...").to_dict(),
            )


@with_logger_configuration(_logger, __name__)
def handle_session_clearing():
    """
    Sent by the client when after acknowledging the end of a match.
    Clears all the match related session variables so they may queue for a new match.
    """
    session_utils.clear_match_info()
