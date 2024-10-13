from flask import session
from flask_socketio import emit, join_room, leave_room

from config.logger import logger
from constants.session_variables import PLAYER_INFO, ROOM_ID, SESSION_ID
from dto.client_stored_match_info_dto import ClientStoredMatchInfoDto
from dto.queue_player_dto import QueuePlayerDto
from dto.server_only.player_info_dto import PlayerInfoDto
from events.events import Events
from exceptions.queue_error import QueueError
from handlers import match_handler, room_handler
from utils.id_generation_utils import generate_id


def handle_queue_registration(data: dict):
    """
    Handles match making requests, starting with the queue-register event.

    Is in charge of creating the room up to creating the match.
    """
    if session.get(SESSION_ID) is None:
        logger.debug("Attempting to register with no initiated session, denying")
        raise QueueError(
            "Something went wrong, please refresh the page and try again",
            socket_connection_killer=True,
        )

    if session.get(ROOM_ID) is not None:
        logger.debug("Already in a room, ignoring registration request")
        raise QueueError(
            "You are already registered in the queue", socket_connection_killer=True
        )

    if room_handler.at_capacity():
        logger.info("Room handler at maximum capacity, denying queue registration")
        raise QueueError(
            "The server has reached its maximum capacity, please try again later",
            socket_connection_killer=True,
        )

    queue_player_dto = QueuePlayerDto.from_dict(data)
    player_id = set_player_id(queue_player_dto)

    logger.info(
        f"{Events.SERVER_QUEUE_REGISTERED.name} event : {queue_player_dto.playerId}"
    )

    (room_id, closed) = make_enter_in_room(queue_player_dto)

    # The room in which the player entered already had a player waiting.
    # In that case, initiate the match, and notify both clients that an opponent was found.
    if closed:
        mhu = match_handler.initiate_match(room_handler.closed_rooms[room_id])
        match_info = mhu.match_info
        # save the player info in the session
        save_player_info(match_info.player2)
        # Notify the room that the match can start
        emit(Events.SERVER_QUEUE_OPPONENT_FOUND.value, to=room_id, broadcast=True)
        mhu.watch_player_entry()
    else:
        player_info = PlayerInfoDto(player_id, True, queue_player_dto.user)
        save_player_info(player_info)


def set_player_id(queue_player_dto: QueuePlayerDto):
    """
    Sets the player id and saves it into the session.
    """
    player_id = generate_id(QueuePlayerDto)
    queue_player_dto.playerId = player_id

    return player_id


def make_enter_in_room(queue_player_dto: QueuePlayerDto):
    """
    Set the session's room id and notifies the client that the player is registered in a room.
    """
    (room, closed) = room_handler.make_enter_in_room(queue_player_dto)
    if not room.sessionIds:
        room.sessionIds = {queue_player_dto.playerId: session[SESSION_ID]}
    else:
        room.sessionIds[queue_player_dto.playerId] = session[SESSION_ID]

    room_id = room.id

    session[ROOM_ID] = room_id
    join_room(room_id)

    emit(
        Events.SERVER_QUEUE_REGISTERED.value,
        ClientStoredMatchInfoDto(queue_player_dto.playerId, room_id).to_dict(),
    )  # Notify the client that registration succeeded, sending them their player id and room id

    return room_id, closed


def save_player_info(player_info: PlayerInfoDto):
    """
    Saves the player information into the session.
    """
    session[PLAYER_INFO] = player_info
    session.modified = True
