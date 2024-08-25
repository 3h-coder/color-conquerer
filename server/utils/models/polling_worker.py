import asyncio
import multiprocessing

from config.logger import logger
from utils.models.dillprocess import DillProcess


class PollingWorker:
    POLLING_DELAY_IN_S = 0.05  # 50ms

    def __init__(self, queue: multiprocessing.Queue, consumer_method, *args, **kwargs):
        self.queue = queue
        self.consumer_method = consumer_method
        self.args = args
        self.kwargs = kwargs
        self.process = DillProcess(target=start_polling, args=(self,))
        self.process.daemon = True

    async def poll(self):
        while True:
            if not self.queue.empty():
                logger.debug("Exit watcher generation queue not empty")
                item = self.queue.get()
                logger.debug(f"Item is {item}")
                self.consumer_method(item, *self.args, **self.kwargs)
            else:
                await asyncio.sleep(self.POLLING_DELAY_IN_S)

    def launch_polling(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.poll())

    def start(self):
        self.process.start()


def start_polling(polling_worker: PollingWorker):
    polling_worker.launch_polling()
