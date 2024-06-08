from config.logger import logger
from dto.queue_register_dto import QueueRegisterDto


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

        self.queue.append(data.idInQueue)

    def withdraw(self, data: QueueRegisterDto):
        """
        Withdraws the player from the queue.
        """

        try:
            self.queue.remove(data.idInQueue)
        except ValueError:
            pass
