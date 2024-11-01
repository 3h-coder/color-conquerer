from multiprocessing import Process, Value
from time import sleep


class TimeStorerSeconds:
    """
    Class in which we will be able to retrive the remaining time of a countdown.
    """

    def __init__(self):
        # Using a shared memory variable to store remaining time (in seconds)
        self.remaining_time = Value("i", 0)  # 'i' stands for integer
        self._process = None

    def _tick(self, duration_in_s):
        """Private method to count down in a separate process."""
        # Initialize the timer
        self.remaining_time.value = duration_in_s
        while self.remaining_time.value > 0:
            sleep(1)
            with self.remaining_time.get_lock():  # Lock to safely update the variable
                self.remaining_time.value -= 1

    def start_timer(self, duration_in_s):
        """Starts the timer in a separate process."""
        self.stop_timer()

        self._process = Process(target=self._tick, args=(duration_in_s,))
        self._process.start()

    def stop_timer(self):
        """Stops the timer process if it's running."""
        if self._process and self._process.is_alive():
            self._process.terminate()
            self._process.join()
            with self.remaining_time.get_lock():
                self.remaining_time.value = 0

    def get_remaining_time(self):
        """Gets the remaining time in seconds."""
        return self.remaining_time.value
