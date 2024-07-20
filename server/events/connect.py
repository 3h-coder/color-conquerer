from flask import session

from config.config import logger


def handle_connection():
    session["connected"] = True
    logger.debug("Session connection")
