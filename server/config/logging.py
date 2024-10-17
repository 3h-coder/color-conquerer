import logging
import os
from functools import wraps
from logging.handlers import TimedRotatingFileHandler

from config import logs_root_path
from utils import os_utils


def with_logger_configuration(logger, name: str, file_name: str = None):
    """
    Configures the given logger before calling the function if it is not initialized.

    :param name: The name of the logger (usually class or module).
    :param file_name: Optional log file name. If not provided, defaults to the logger name.
    """

    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            nonlocal logger
            if logger is None:
                logger = get_configured_logger(name, file_name)
            function(*args, **kwargs)

        return wrapper

    return decorator


def get_configured_logger(name: str, file_name: str = None):
    """
    Creates a logger with the given name and sets up file & console handlers.
    Logs are saved in the 'logs' directory, and a log file name can be specified.

    :param name: The name of the logger (usually class or module).
    :param file_name: Optional log file name. If not provided, defaults to the logger name.
    :return: Configured logger instance.
    """

    LOG_EXTENSION = ".log"
    name = name.strip()
    file_name = file_name.strip() if file_name and file_name.strip() else name

    if not file_name.endswith(LOG_EXTENSION):
        file_name = f"{file_name}{LOG_EXTENSION}"

    LOG_FILE_PATH = os.path.join(logs_root_path, file_name)

    os_utils.create_dir_if_not_exists(LOG_FILE_PATH)

    logger = logging.getLogger(name)

    # Avoid adding handlers multiple times in case the logger is retrieved again
    if not logger.handlers:
        handler = TimedRotatingFileHandler(
            LOG_FILE_PATH, when="midnight", interval=1, backupCount=120
        )
        formatter = logging.Formatter(
            "%(asctime)s.%(msecs)03d | %(name)s | %(levelname)s | %(message)s",  # Include logger name
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        handler.setFormatter(formatter)
        logger.addHandler(handler)
        if logger.name == "root":
            logger.addHandler(logging.StreamHandler())

        # TODO: handle the level dynamically
        logger.setLevel(logging.DEBUG)

    return logger


root_logger = get_configured_logger("root")
