import time
from functools import wraps
from time import perf_counter
from typing import Any, Callable

from config.logging import get_configured_logger

_perf_logger = get_configured_logger("performance_logging")


def with_performance_logging(func):
    """
    Decorator method to log the time a function takes to execute.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = perf_counter()
        result = func(*args, **kwargs)
        end_time = perf_counter()

        execution_time = (end_time - start_time) * 1000  # Convert to milliseconds
        _perf_logger.info(
            f"Function '{func.__name__}' took {execution_time:.2f}ms to execute"
        )

        return result

    return wrapper


def wait_until(
    condition: Callable[[], bool],
    timeout_in_s: float = 1.0,
    poll_interval_in_s: float = 0.01,
):
    start = time.time()
    while not condition() and time.time() - start < timeout_in_s:
        time.sleep(poll_interval_in_s)
    assert condition(), "Timeout waiting for condition"
