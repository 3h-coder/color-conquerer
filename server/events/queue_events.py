from flask import session
from flask_socketio import emit, join_room

from ai import AI_PLAYER_USERNAME
from config.logging import get_configured_logger
from dto.match.client_stored_match_info_dto import ClientStoredMatchInfoDto
from dto.player.queue_player_dto import QueuePlayerDto
from dto.player.user_dto import UserDto
from events.events import Events
from exceptions.queue_error import QueueError
from game_engine.models.dtos.room import Room
from handlers.room_handler import RoomHandler
from handlers.session_cache_handler import SessionCacheHandler
from persistence.session import session_utils
from persistence.session.models.session_player import SessionPlayer
from persistence.session.session_variables import PLAYER_INFO, ROOM_ID, SESSION_ID
from server_gate import get_match_handler, get_room_handler, get_session_cache_handler
from utils import logging_utils
from utils.id_generation_utils import generate_id

_logger = get_configured_logger(
    __name__, prefix_getter=lambda: logging_utils.flask_request_remote_addr_prefix()
)


def handle_queue_registration(data: dict):
    """
    Handles match making requests, starting with the queue-register event.

    Is in charge of creating the room up to creating the match.
    """
    session_utils.refresh_session_lifetime(logger=_logger)
    room_handler = get_room_handler()
    session_cache_handler = get_session_cache_handler()

    _raise_possible_errors(room_handler)

    queue_player_dto = QueuePlayerDto.from_dict(data)
    player_id = _set_player_id(queue_player_dto)

    _logger.info(
        f"{Events.SERVER_QUEUE_REGISTERED.name} event : {queue_player_dto.playerId}"
    )

    (room, closed) = _make_enter_in_room(queue_player_dto, room_handler)
    room_id = room.id
    is_player1 = not closed

    player_info = SessionPlayer(
        player_id=player_id,
        is_player1=is_player1,
        individual_room_id=room.player1_room_id if is_player1 else room.player2_room_id,
    )
    _save_into_session(room_id, player_info, session_cache_handler)

    # Initiate the match if the room is closed
    if closed:
        match_handler = get_match_handler()
        match_handler.notify_clients_and_initiate_match(room)


def handle_ai_queue_registration(data: dict):
    """
    Handles AI match requests. Creates a room with the human player and an AI opponent,
    then immediately starts the match.
    """
    session_utils.refresh_session_lifetime(logger=_logger)
    room_handler = get_room_handler()
    session_cache_handler = get_session_cache_handler()

    _raise_possible_errors(room_handler)

    queue_player_dto = QueuePlayerDto.from_dict(data)
    player_id = _set_player_id(queue_player_dto)

    _logger.info(
        f"{Events.CLIENT_QUEUE_AI_REGISTER.name} event : {queue_player_dto.playerId}"
    )

    # Create AI player
    ai_queue_dto = _create_ai_player_dto()

    # Create a room with both players
    room = _create_ai_room(queue_player_dto, ai_queue_dto, room_handler)

    # Save player info for the human player
    player_info = SessionPlayer(
        player_id=player_id,
        is_player1=True,
        individual_room_id=room.player1_room_id,
    )
    _save_into_session(room.id, player_info, session_cache_handler)

    join_room(room.id)

    emit(
        Events.SERVER_QUEUE_REGISTERED,
        ClientStoredMatchInfoDto(queue_player_dto.playerId, room.id).to_dict(),
    )

    # Initiate the match immediately
    match_handler = get_match_handler()
    match_handler.notify_clients_and_initiate_match(room)


def _raise_possible_errors(room_handler: RoomHandler):
    """
    Checks if registration is possible, and if not, raises the adequate error.
    """

    if session.get(SESSION_ID) is None:
        _logger.debug(f"Attempting to register with no initiated session, denying")
        raise QueueError(
            QueueError.NO_SESSION_ERROR_MSG,
            socket_connection_killer=True,
        )

    if session.get(ROOM_ID) is not None:
        _logger.debug(f"Already in a room, ignoring registration request")
        raise QueueError(
            QueueError.ALREADY_REGISTERED_ERROR_MSG, socket_connection_killer=True
        )

    if room_handler.at_capacity():
        _logger.info(f"Room handler at maximum capacity, denying queue registration")
        raise QueueError(
            QueueError.MAX_CAPACITY_ERROR_MSG,
            socket_connection_killer=True,
        )


def _set_player_id(queue_player_dto: QueuePlayerDto):
    """
    Sets the player id and saves it into the session.
    """
    player_id = generate_id(QueuePlayerDto)
    queue_player_dto.playerId = player_id

    return player_id


def _make_enter_in_room(queue_player_dto: QueuePlayerDto, room_handler: RoomHandler):
    """
    Set the session's room id and notifies the client that the player is registered in a room.
    """
    (room, closed) = room_handler.make_enter_in_room(queue_player_dto)
    if not room.session_ids:
        room.session_ids = {session[SESSION_ID]: queue_player_dto.playerId}
    else:
        room.session_ids[session[SESSION_ID]] = queue_player_dto.playerId

    room_id = room.id
    join_room(room_id)

    emit(
        Events.SERVER_QUEUE_REGISTERED,
        ClientStoredMatchInfoDto(queue_player_dto.playerId, room_id).to_dict(),
    )  # Notify the client that registration succeeded, sending them their player id and room id

    return room, closed


def _save_into_session(
    room_id: str, player_info: SessionPlayer, session_cache_handler: SessionCacheHandler
):
    """
    Saves the player information into the session.
    """
    session_cache = session_cache_handler.get_cache_for_session(session.get(SESSION_ID))
    session[ROOM_ID] = session_cache[ROOM_ID] = room_id
    session[PLAYER_INFO] = session_cache[PLAYER_INFO] = player_info.to_dict()
    session_utils.forcefully_save_session()


def _create_ai_player_dto() -> QueuePlayerDto:
    """
    Creates a synthetic QueuePlayerDto for the AI opponent.
    """
    ai_player_id = generate_id(QueuePlayerDto)
    return QueuePlayerDto(
        user=UserDto(
            id="", username=AI_PLAYER_USERNAME, isAuthenticating=False, isAuthenticated=False
        ),
        playerId=ai_player_id,
    )


def _create_ai_room(
    human_player_dto: QueuePlayerDto,
    ai_player_dto: QueuePlayerDto,
    room_handler: RoomHandler,
) -> Room:
    """
    Creates a closed room with a human player and an AI opponent.
    """
    room_id = generate_id(Room)
    room = Room(
        id=room_id,
        player1_queue_dto=human_player_dto,
        player2_queue_dto=ai_player_dto,
        player1_room_id=f"{room_id}-p1",
        player2_room_id=f"{room_id}-p2",
        session_ids={session[SESSION_ID]: human_player_dto.playerId},
    )

    room_handler.closed_rooms[room_id] = room
    room_handler._log_rooms_count()

    return room
