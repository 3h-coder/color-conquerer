from flask import session
from flask_socketio import emit, join_room, leave_room

from config.logger import logger
from dto.queue_player_dto import QueuePlayerDto
from events.events import Events
from exceptions.queue_error import QueueError
from handlers import match_handler, room_handler


def handle_match_request(data: dict):
    """
    Handles match making requests, starting with the queue-register event.

    Is in charge of creating the room up to creating the match.
    """
    try:
        if room_handler.at_capacity():
            logger.info("Room handler at maximum capacity, denying queue registration")
            emit(Events.SERVER_QUEUE_FULL)
            return

        queue_player_dto = QueuePlayerDto.from_dict(data)
        logger.info(
            f"{Events.SERVER_QUEUE_REGISTERED.name} event : {queue_player_dto.playerId}"
        )

        (room_id, closed) = make_enter_in_room(queue_player_dto)

        # The room in which the player entered already had a player waiting,
        # notify both clients that an opponent was found and create the match.
        if closed:
            initiate_match(room_id)

    except Exception as ex:
        logger.error(f"An error occured match request : {ex}")
        raise QueueError(f"An error occured during match request : {ex}")


def handle_queue_withdrawal(data: dict):
    """
    Handles the queue-withdrawal event.
    """
    try:
        queue_register_dto = QueuePlayerDto.from_dict(data)
        logger.info(
            f"{Events.CLIENT_QUEUE_WITHDRAWAL.name} event : {queue_register_dto.playerId}"
        )

        room_id = session["room_id"]
        leave_room(room_id)

        # Technically, only open rooms allow queue-withdrawal,
        # leaving a closed room automatically leads to match ending
        room_handler.remove_room(room_id)

    except Exception as ex:
        logger.error(f"An error occured during queue withdrawal : {ex}")
        raise QueueError()


def make_enter_in_room(queue_player_dto: QueuePlayerDto):
    """
    Set the session's room id and notifies the client that the player is registered in a room.
    """
    (room_id, closed) = room_handler.make_enter_in_room(queue_player_dto)

    session["room_id"] = room_id
    join_room(room_id)

    emit(
        Events.SERVER_QUEUE_REGISTERED.value
    )  # Notify the client that registration succeeded

    return room_id, closed


def initiate_match(room_id: str):
    """
    Notifies the client that an opponent was found, initiates the match and notifies the client again.
    """
    emit(Events.SERVER_QUEUE_OPPONENT_FOUND.value, to=room_id, broadcast=True)

    match_handler_unit = match_handler.initiate_match(
        room_handler.closed_rooms[room_id]
    )
    emit(
        Events.SERVER_MATCH_READY.value,
        match_handler_unit.match_info.to_json(),
        to=room_id,
        broadcast=True,
    )
