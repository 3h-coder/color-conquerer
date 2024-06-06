import logging
import os
from logging.handlers import TimedRotatingFileHandler

from config import root_path
from utils import os_utils

LOG_FILE_PATH = os.path.join(root_path, "logs", "global.log")


def _get_configured_logger():
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


os_utils.create_dir_if_not_exists(LOG_FILE_PATH)
logger = _get_configured_logger()
