from flask import request, session
from flask_socketio import emit, join_room

from config.logging import get_configured_logger
from constants.session_variables import IN_MATCH, PLAYER_INFO, ROOM_ID, SESSION_ID
from dto.message_dto import MessageDto
from dto.server_only.player_info_dto import PlayerInfoDto
from dto.turn_info_dto import TurnInfoDto
from events.events import Events
from exceptions.server_error import ServerError
from handlers import match_handler, session_cache_handler
from utils import session_utils

_logger = get_configured_logger(__name__)


def handle_client_ready():
    """
    Marks the given player (i.e. the client sending emitting the event)
    as ready, possibly  starting the match if everyone is.
    """
    player_info: PlayerInfoDto = session.get(PLAYER_INFO)
    if player_info is None:
        _logger.error(
            f"({request.remote_addr}) | player_info was None, resorting to session cache"
        )
        session_cache = session_cache_handler.get_cache_for_session(session[SESSION_ID])
        player_info = session_cache.get(PLAYER_INFO)
        if player_info is None:
            raise ServerError(
                "A server error occured, unable to connect you to your match",
                socket_connection_killer=True,
            )

    room_id = session.get(ROOM_ID)
    if room_id is None:
        _logger.error(
            f"({request.remote_addr}) | room_id was None, resorting to session cache"
        )
        session_cache = session_cache_handler.get_cache_for_session(session[SESSION_ID])
        room_id = session_cache.get(ROOM_ID)
        if room_id is None:
            raise ServerError(
                "A server error occured, unable to connect you to your match",
                socket_connection_killer=True,
            )

    join_room(room_id)
    mhu = match_handler.get_unit(room_id)
    mhu.players_ready[player_info.playerId] = True
    session[IN_MATCH] = True

    # The start match event is what the client uses to render the game
    if mhu.is_ongoing():
        emit(
            Events.SERVER_MATCH_STARTED.value,
            TurnInfoDto(
                mhu.match_info.isPlayer1Turn, mhu.turn_time_storer.get_remaining_time()
            ).to_dict(),
        )
    elif mhu.is_waiting_to_start():
        if all(value is True for value in mhu.players_ready.values()):
            _logger.info(f"All players ready in the room {room_id}")
            mhu.start_match()
            # TODO : This emit should be in start match
            emit(
                Events.SERVER_MATCH_STARTED.value,
                TurnInfoDto(
                    mhu.match_info.isPlayer1Turn,
                    mhu.turn_time_storer.get_remaining_time(),
                ).to_dict(),
                to=room_id,
                broadcast=True,
            )
        else:
            emit(
                Events.SERVER_SET_WAITING_TEXT.value,
                MessageDto.from_string("Waiting for your opponent...").to_dict(),
            )


def handle_session_clearing():
    """
    Sent by the client when after acknowledging the end of a match.
    Clears all the match related session variables so they may queue for a new match.
    """
    session_utils.clear_match_info()
