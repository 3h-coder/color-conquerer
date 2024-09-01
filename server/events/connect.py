from flask import session

from config.config import logger
from constants.session_variables import PLAYER_INFO, ROOM_ID, SOCKET_CONNECTED
from handlers import match_handler
from handlers.match_handler_unit import MatchStatus


def handle_connection(data):
    # logger.debug(f"Connection data is {data}")

    session[SOCKET_CONNECTED] = True
    logger.debug("----- Socket connection -----")

    room_id = session.get(ROOM_ID)
    if not room_id:
        return

    mhu = match_handler.get_unit(room_id)

    if mhu.is_ongoing():
        logger.debug("Player rejoinded the match, stopping exit watcher")
        player_id = session.get(PLAYER_INFO).playerId
        mhu.stop_watching_player_exit(player_id)
    elif mhu.is_ended():
        logger.debug("Player rejoined, but the match already ended")
