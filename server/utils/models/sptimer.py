import time

from config.logger import logger
from utils.models.dillprocess import DillProcess


class SPTimer:
    """
    Wrapper class around a daemon process to behave as a timer and periodically execute a function.
    """

    def __init__(
        self,
        paused_event,
        stopped_event,
        tick_interval,
        on_tick,
        on_tick_args=None,
        tick_instantly=False,
        max_ticks=None,
    ):
        """
        Initializes the Timer.

        :param paused_event: Event object used to set the timer as paused.
        :param stopped_event: Event object used to set the timer as stopped.
        :param tick_interval: Time interval between each tick (in seconds). Its value must be `>= 0.3`.
        :param on_tick: The function to execute on each tick.
        :param max_ticks: Maximum number of ticks (optional). If None, it will tick indefinitely.
        """
        if max_ticks is not None and max_ticks <= 0:
            raise ValueError("The max_ticks variable cannot be inferior or equal to 0")

        if tick_interval < 0.3:
            raise ValueError(
                "The timer must have a tick interval of at least 0.3 seconds"
            )

        self.tick_interval = tick_interval
        self.on_tick = on_tick
        self.on_tick_args = on_tick_args
        self.tick_instantly = tick_instantly
        self.max_ticks = max_ticks
        self.current_ticks = 0
        # Use a multiprocessing.Manager to create shared events -> https://stackoverflow.com/questions/9908781/sharing-a-result-queue-among-several-processes
        self.paused = paused_event
        self.stopped = stopped_event
        self.process = None  # We do not initialize the process now as it prevents the instance from being pickled and thefore passed in multiprocessing queues

    def _initialize_process(self):
        # Using self.run triggers a type error as a DillProcess cannot be pickled, we therefore resort to this
        self.process = DillProcess(target=run_timer, args=(self,))
        self.process.daemon = True

    def run(self):
        logger.debug("Called SPTimer.run()")

        while not self.stopped.is_set():
            if self.paused.is_set():
                self._polling_sleep(self.tick_interval)
                continue

            if self.current_ticks == 0 and not self.tick_instantly:
                # Wait for the first interval if not ticking instantly
                self._polling_sleep(self.tick_interval)

            self._trigger_tick()
            self._polling_sleep(self.tick_interval)

        logger.debug("The timer was stopped")

    def _trigger_tick(self):
        if self.stopped.is_set():
            return

        self.current_ticks += 1

        if self.on_tick_args:
            self.on_tick(*self.on_tick_args)
        else:
            self.on_tick()

        if self.max_ticks and self.current_ticks >= self.max_ticks:
            self.stop()

    def _polling_sleep(self, duration):
        """Sleep for `duration` seconds, checking periodically if stopped."""
        time_period_in_s = 0.1  # Check every 100ms
        elapsed = 0
        while elapsed < duration:
            if self.stopped.is_set():
                return
            time.sleep(time_period_in_s)
            elapsed += time_period_in_s

    def start(self):
        """Start the timer."""
        if (
            self.process is None
            or self.process.pid is None
            or not self.process.is_alive()
        ):
            self._initialize_process()
        self.stopped.clear()
        self.process.start()

    def pause(self):
        """Pause the timer."""
        self.paused.set()

    def resume(self):
        """Resume the timer."""
        self.paused.clear()

    def stop(self):
        """Stop the timer."""
        self.stopped.set()
        # Sometimes the process is stopped before it could even be started
        if self.process is None:
            return


def run_timer(sp_timer: SPTimer):
    sp_timer.run()
