import multiprocessing
import time


class SPTimer:
    """
    Wrapper class around a `multiprocessing.Process` object to periodically execute a function.
    """

    def __init__(self, tick_interval, on_tick, tick_instantly=False, max_ticks=None):
        """
        Initialize the Timer.

        :param tick_interval: Time interval between each tick (in seconds).
        :param on_tick: The function to execute on each tick.
        :param max_ticks: Maximum number of ticks (optional). If None, it will tick indefinitely.
        """
        if max_ticks is not None and max_ticks <= 0:
            raise ValueError("The max_ticks variable cannot be inferior or equal to 0")

        self.tick_interval = tick_interval
        self.on_tick = on_tick
        self.tick_instantly = tick_instantly
        self.max_ticks = max_ticks
        self.current_ticks = 0
        self.paused = multiprocessing.Event()
        self.stopped = multiprocessing.Event()
        self.process = multiprocessing.Process(target=self._run)

    def _run(self):
        while not self.stopped.is_set():
            if not self.paused.is_set():
                if self.current_ticks == 0 and not self.tick_instantly:
                    time.sleep(
                        self.tick_interval
                    )  # Wait for the first interval if not ticking instantly
                # Check if the timer was stopped during the initial delay
                if self.stopped.is_set():
                    return
                self._trigger_tick()  # Perform the tick
            time.sleep(self.tick_interval)

    def _trigger_tick(self):
        self.current_ticks += 1
        self.on_tick()
        if self.max_ticks and self.current_ticks >= self.max_ticks:
            self.stop()

    def start(self):
        """Start the timer."""
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
        self.process.join()
        self.process.close()

    def is_alive(self):
        """Check if the timer is still running."""
        return self.process.is_alive()
