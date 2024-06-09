from config.logger import logger
from dto.queue_register_dto import QueueRegisterDto
from handlers import room_handler


class QueueHandler:
    """
    Class responsible for handling the queueing system for
    when players are searching for an opponent.
    """

    def __init__(self):
        self.queue: list[str] = []

    def register(self, data: QueueRegisterDto):
        """
        Registers the incoming data into the queue for
        processing.
        """
        try:
            self.queue.append(data.playerId)
            logger.debug(f"Queue : {self.queue}")

            return True
        except Exception:
            return False

    def withdraw(self, data: QueueRegisterDto):
        """
        Withdraws the player from the queue.
        """
        try:
            self.queue.remove(data.playerId)
            logger.debug(f"Queue : {self.queue}")

            # TODO: remove the room from room_handler.open_rooms
        except ValueError:
            pass
