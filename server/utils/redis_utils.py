import logging
import socket

import redis

from config import config
from config.variables import OptionalVariable

REDIS_HOST = "localhost"


def is_redis_up_and_running(logger: logging.Logger):
    """
    Checks if a socket connection can be established to the port that redis is
    assigned to in the configuration.
    """
    port = config.get(OptionalVariable.APP_REDIS_SERVER_PORT)
    logger.info(
        f"Checking if a socket connection can be established to the Redis port ({port})"
    )

    try:
        with socket.create_connection((REDIS_HOST, port), timeout=2):
            logger.info(f"Redis is running on {REDIS_HOST}:{port}")
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        logger.warning(f"Redis is NOT running on {REDIS_HOST}:{port}")
        return False


def create_connection(logger: logging.Logger):
    """
    Returns a redis.Redis instance, using localhost as the host and the port defined in the
    configuration.
    """
    port = config.get(OptionalVariable.APP_REDIS_SERVER_PORT)
    logger.info("Creating a redis instance")

    return redis.StrictRedis(host=REDIS_HOST, port=port)
