import asyncio

from config.logger import logger
from utils.models.dillprocess import DillProcess


class PollingWorker:
    """
    Wrapper class around a daemon process that will continuously poll a multiprocessing queue
    to execute a function from the provided arguments.
    """

    POLLING_DELAY_IN_S = 0.05  # 50ms

    def __init__(self, consumer_method, queue):
        self.consumer_method = consumer_method
        self.arguments_queue = queue
        self.process = DillProcess(target=start_polling, args=(self,))
        self.process.daemon = True
        self.started = False

    async def poll(self):
        while True:
            if not self.arguments_queue.empty():
                # logger.debug("Exit watcher generation queue not empty")
                args, kwargs = self.arguments_queue.get()
                # logger.debug(f"The args are {args} | kwargs are {kwargs}")
                self.consumer_method(*args, **kwargs)
            else:
                await asyncio.sleep(self.POLLING_DELAY_IN_S)

    def launch_polling(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.poll())

    def start(self):
        self.process.start()
        self.started = True

    def is_alive(self):
        return self.process.is_alive()


def start_polling(polling_worker: PollingWorker):
    polling_worker.launch_polling()
