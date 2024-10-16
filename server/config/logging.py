import logging
import os
from logging.handlers import TimedRotatingFileHandler

from config import logs_root_path
from utils import os_utils


def get_configured_logger(file_name: str):
    LOG_EXTENSION = ".log"

    if not file_name.endswith(LOG_EXTENSION):
        file_name = f"{file_name}{LOG_EXTENSION}"

    LOG_FILE_PATH = os.path.join(logs_root_path, file_name)

    os_utils.create_dir_if_not_exists(LOG_FILE_PATH)

    logger = logging.getLogger()

    handler = TimedRotatingFileHandler(
        LOG_FILE_PATH, when="midnight", interval=1, backupCount=120
    )
    formatter = logging.Formatter(
        "%(asctime)s.%(msecs)03d | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.addHandler(logging.StreamHandler())

    # TODO: handle the level dynamically
    logger.setLevel(logging.DEBUG)

    return logger


root_logger = get_configured_logger("global")
