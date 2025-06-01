import logging
import os
from logging.handlers import TimedRotatingFileHandler
from typing import Any, Callable

from config import logs_root_path, test_logs_root_path
from utils import os_utils

_testing = False

ROOT_LOGGER_NAME = "root"


def enable_test_mode_for_logging():
    global _testing
    _testing = True


class PrefixFilter(logging.Filter):
    def __init__(self, prefix_getter: Callable[[Any], str]):
        super().__init__()
        self.prefix_getter = prefix_getter

    def filter(self, record: logging.LogRecord):
        prefix = self.prefix_getter() if self.prefix_getter else None
        record.prefix = f"{prefix} | " if prefix else ""
        return True


def get_configured_logger(
    name: str, file_name: str = None, prefix_getter: Callable = None
):
    """
    Creates a logger with the given name and sets up file & console handlers.
    Logs are saved in the 'logs' directory, and a log file name can be specified.

    :param name: The name of the logger (usually class or module).
    :param file_name: Optional log file name. If not provided, defaults to the logger name.
    :param prefix_getter: Callable that returns the prefix string at runtime.
    :return: Configured logger instance.
    """
    global _testing

    LOG_EXTENSION = ".log"
    name = name.strip()
    file_name = file_name.strip() if file_name and file_name.strip() else name

    if not file_name.endswith(LOG_EXTENSION):
        file_name = f"{file_name}{LOG_EXTENSION}"

    root_path = logs_root_path if not _testing else test_logs_root_path
    LOG_FILE_PATH = os.path.join(root_path, file_name)

    os_utils.create_dir_if_not_exists(LOG_FILE_PATH)

    logger = logging.getLogger(name)

    # Avoid adding handlers multiple times in case the logger is retrieved again
    if not logger.handlers:
        handler = TimedRotatingFileHandler(
            LOG_FILE_PATH, when="midnight", interval=1, backupCount=120
        )
        fmt = (
            "%(asctime)s.%(msecs)03d | %(name)s | %(levelname)s | %(prefix)s%(message)s"
        )
        formatter = logging.Formatter(
            fmt,
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        handler.setFormatter(formatter)
        handler.addFilter(PrefixFilter(prefix_getter))
        logger.addHandler(handler)

        if logger.name == ROOT_LOGGER_NAME:
            logger.addHandler(logging.StreamHandler())
        else:
            from utils import logging_utils

            # Note : The root logger's logging level is re-adjusted
            # right after the config gets loaded
            logging_utils.set_logging_level_from_config(logger)

    return logger


root_logger = get_configured_logger(ROOT_LOGGER_NAME)
