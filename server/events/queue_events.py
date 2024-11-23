from flask import request, session
from flask_socketio import emit, join_room

from config.logging import get_configured_logger
from constants.session_variables import PLAYER_INFO, ROOM_ID, SESSION_ID
from dto.client_stored_match_info_dto import ClientStoredMatchInfoDto
from dto.queue_player_dto import QueuePlayerDto
from dto.server_only.error_dto import ErrorDto
from dto.server_only.player_info_dto import PlayerInfoDto
from events.events import Events
from exceptions.queue_error import QueueError
from handlers import match_handler, room_handler, session_cache_handler
from handlers.match_helpers.match_handler_unit import MatchHandlerUnit
from server_gate import get_server
from utils import session_utils
from utils.id_generation_utils import generate_id

_logger = get_configured_logger(__name__)


def handle_queue_registration(data: dict):
    """
    Handles match making requests, starting with the queue-register event.

    Is in charge of creating the room up to creating the match.
    """
    _raise_possible_errors()

    queue_player_dto = QueuePlayerDto.from_dict(data)
    player_id = _set_player_id(queue_player_dto)

    _logger.info(
        f"({request.remote_addr}) | {Events.SERVER_QUEUE_REGISTERED.name} event : {queue_player_dto.playerId}"
    )

    (room_id, closed) = _make_enter_in_room(queue_player_dto)
    player_info = PlayerInfoDto(
        player_id, isPlayer1=not closed, user=queue_player_dto.user, playerGameInfo=None
    )
    _save_into_session(room_id, player_info)

    # If the room is closed, then it already had a player waiting.
    # In that case, initiate the match, and notify both clients that an opponent was found.
    if closed:
        _try_to_launch_match(room_id)


def _raise_possible_errors():
    """
    Checks if registration is possible, and if not, raises the adequate error.
    """

    if session.get(SESSION_ID) is None:
        _logger.debug(
            f"({request.remote_addr}) | Attempting to register with no initiated session, denying"
        )
        raise QueueError(
            "Something went wrong, please refresh the page and try again",
            socket_connection_killer=True,
        )

    if session.get(ROOM_ID) is not None:
        _logger.debug(
            f"({request.remote_addr}) | Already in a room, ignoring registration request"
        )
        raise QueueError(
            "You are already registered in the queue", socket_connection_killer=True
        )

    if room_handler.at_capacity():
        _logger.info(
            f"({request.remote_addr}) | Room handler at maximum capacity, denying queue registration"
        )
        raise QueueError(
            "The server has reached its maximum capacity, please try again later",
            socket_connection_killer=True,
        )


def _try_to_launch_match(room_id):
    """
    Tries to launch a match, saving the second player's session information at the same time.
    """
    match: MatchHandlerUnit = None
    server = get_server()
    try:
        match = match_handler.initiate_match_and_return_unit(
            room_handler.closed_rooms[room_id]
        )
        match.watch_player_entry()
        # Notify the room that the match can start, it will be started once all players are ready
        emit(Events.SERVER_QUEUE_OPPONENT_FOUND.value, to=room_id, broadcast=True)
    except Exception as ex:
        _logger.exception(f"An error occured when trying to launch a match : {ex}")
        if match is not None:
            match.cancel()
        room_handler.remove_closed_room(room_id)
        # The disconnection should clear the session allowing players to re apply for a match

        server.socketio.emit(
            Events.SERVER_ERROR.value,
            ErrorDto(
                "An error occured, please try again",
                displayToUser=True,
                socketConnectionKiller=True,
            ).to_dict(),
            to=room_id,
        )


def _set_player_id(queue_player_dto: QueuePlayerDto):
    """
    Sets the player id and saves it into the session.
    """
    player_id = generate_id(QueuePlayerDto)
    queue_player_dto.playerId = player_id

    return player_id


def _make_enter_in_room(queue_player_dto: QueuePlayerDto):
    """
    Set the session's room id and notifies the client that the player is registered in a room.
    """
    (room, closed) = room_handler.make_enter_in_room(queue_player_dto)
    if not room.sessionIds:
        room.sessionIds = {session[SESSION_ID]: queue_player_dto.playerId}
    else:
        room.sessionIds[session[SESSION_ID]] = queue_player_dto.playerId

    room_id = room.id
    join_room(room_id)

    emit(
        Events.SERVER_QUEUE_REGISTERED.value,
        ClientStoredMatchInfoDto(queue_player_dto.playerId, room_id).to_dict(),
    )  # Notify the client that registration succeeded, sending them their player id and room id

    return room_id, closed


def _save_into_session(room_id: str, player_info: PlayerInfoDto):
    """
    Saves the player information into the session.
    """
    session_cache = session_cache_handler.get_cache_for_session(session.get(SESSION_ID))
    session[ROOM_ID] = session_cache[ROOM_ID] = room_id
    session[PLAYER_INFO] = session_cache[PLAYER_INFO] = player_info
    session.modified = True
