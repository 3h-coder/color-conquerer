import asyncio
import multiprocessing

from config.logger import logger
from utils.models.dillprocess import DillProcess


class PollingWorker:
    POLLING_DELAY_IN_S = 0.05  # 50ms

    def __init__(self, queue: multiprocessing.Queue, consumer_method):
        self.queue = queue
        self.consumer_method = consumer_method
        self.process = DillProcess(target=start_polling, args=(self,))
        self.process.daemon = True
        self.started = False

    async def poll(self):
        while True:
            if not self.queue.empty():
                # logger.debug("Exit watcher generation queue not empty")
                args, kwargs = self.queue.get()
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
