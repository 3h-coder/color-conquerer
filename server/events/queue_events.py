from flask import session
from flask_socketio import emit, join_room

from config.logger import logger
from dto.queue_register_dto import QueueRegisterDto
from events.events import Events
from exceptions.queue_exception import QueueError
from handlers import queue_handler, room_handler


def handle_queue_registration(data: dict):
    """
    Handles the queue-register event.
    """
    try:
        queue_register_dto = QueueRegisterDto.from_dict(data)
        logger.info(
            f"{Events.QUEUE_REGISTERED.name} event : {queue_register_dto.playerId}"
        )

        registration_success = queue_handler.register(queue_register_dto)
        if registration_success:
            emit(Events.QUEUE_REGISTERED.value)
            (room_id, closed) = room_handler.make_enter_in_room(
                queue_register_dto.playerId
            )

            session["room_id"] = room_id
            join_room(room_id)

            if closed:
                emit(Events.QUEUE_OPPONENT_FOUND.value, to=room_id, broadcast=True)

    except Exception as ex:
        logger.error(f"An error occured during queue registration : {ex}")
        raise QueueError()


def handler_queue_withdrawal(data: dict):
    """
    Handles the queue-withdrawal event.
    """

    try:
        queue_register_dto = QueueRegisterDto.from_dict(data)
        logger.info(
            f"{Events.QUEUE_WITHDRAWAL.name} event : {queue_register_dto.playerId}"
        )

        queue_handler.withdraw(queue_register_dto)
        # TODO: Update rooms
    except Exception as ex:
        logger.error(f"An error occured during queue withdrawal : {ex}")
        raise QueueError()
