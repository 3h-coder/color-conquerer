import uuid

from config.config import logger
from dto.room_dto import RoomDto
from handlers.match_handler_unit import MatchHandlerUnit


class MatchHandler:
    """
    Class responsible for monitoring a match between
    2 players.
    """

    def __init__(self):
        self.units: dict[str, MatchHandlerUnit] = {}

    def get_unit(self, match_id):
        try:
            return self.units[match_id]
        except KeyError:
            logger.error(f"No unit currently working for the match : {match_id}")

    def initiate_match(self, room_dto: RoomDto):
        match_handler_unit = MatchHandlerUnit(room_dto)

        match_id = match_handler_unit.match_info.id
        self.units[match_id] = match_handler_unit

        return match_id
