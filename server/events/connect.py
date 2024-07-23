from flask import session

from config.config import logger
from session_variables import SOCKET_CONNECTED


def handle_connection():
    session[SOCKET_CONNECTED] = True
    logger.debug("----- Socket connection -----")
