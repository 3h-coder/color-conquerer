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

    def get_unit(self, unit_id):
        try:
            return self.units[unit_id]
        except KeyError:
            logger.error(f"The following match handler unit does not exist : {unit_id}")

    def initiate_match(self, room_dto: RoomDto):
        match_handler_unit = MatchHandlerUnit(room_dto)
        self.units[match_handler_unit.match_info.id] = match_handler_unit
