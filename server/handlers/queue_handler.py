class QueueHandler:
    """
    Class responsible for handling the queueing system for
    when players are searching for an opponent.
    """

    def __init__(self):
        self.queue: list[str] = []
