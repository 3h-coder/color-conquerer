from flask import session
from flask_socketio import emit, join_room, leave_room

from config.logger import logger
from dto.queue_player_dto import QueuePlayerDto
from events.events import Events
from exceptions.queue_error import QueueError
from handlers import match_handler, room_handler


def handle_queue_registration(data: dict):
    """
    Handles the queue-register event.
    """
    try:
        if room_handler.at_capacity():
            logger.info("Room handler at maximum capacity, denying queue registration")
            emit(Events.QUEUE_FULL)

        queue_register_dto = QueuePlayerDto.from_dict(data)
        logger.info(
            f"{Events.QUEUE_REGISTERED.name} event : {queue_register_dto.playerId}"
        )

        # Make the player enter a room
        (room_id, closed) = room_handler.make_enter_in_room(queue_register_dto)

        emit(
            Events.QUEUE_REGISTERED.value
        )  # Notify the client that registration succeeded

        session["room_id"] = room_id
        join_room(room_id)

        # The room in which the player entered already had a player waiting,
        # notify both clients that an opponent was found
        if closed:
            emit(Events.QUEUE_OPPONENT_FOUND.value, to=room_id, broadcast=True)
            match_handler.initiate_match(room_handler.closed_rooms[room_id])
            session["in_match"] = True

    except Exception as ex:
        logger.error(f"An error occured during queue registration : {ex}")
        raise QueueError(f"An error occured during queue registration : {ex}")


def handle_queue_withdrawal(data: dict):
    """
    Handles the queue-withdrawal event.
    """

    try:
        queue_register_dto = QueuePlayerDto.from_dict(data)
        logger.info(
            f"{Events.QUEUE_WITHDRAWAL.name} event : {queue_register_dto.playerId}"
        )

        room_id = session["room_id"]
        leave_room(room_id)

        # Technically, only open rooms allow queue-withdrawal,
        # leaving a closed room automatically leads to match ending
        room_handler.remove_room(room_id)

    except Exception as ex:
        logger.error(f"An error occured during queue withdrawal : {ex}")
        raise QueueError()
