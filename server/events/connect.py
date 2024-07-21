from flask import session

from config.config import logger


def handle_connection():
    session["socket-connected"] = True
    logger.debug("Socket connection opened")
