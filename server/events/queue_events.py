from config.logger import logger
from dto.queue_register_dto import QueueRegisterDto
from exceptions.queue_exception import QueueError
from handlers import queue_handler


def handle_queue_registration(data: dict):
    """
    Handles the queue-register event.
    """
    try:
        queue_handler.register(QueueRegisterDto.from_dict(data))
    except Exception as ex:
        logger.error(f"An error occured during queueing : {ex}")
        raise QueueError()
