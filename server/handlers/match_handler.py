import uuid

from config.config import logger
from dto.room_dto import RoomDto
from handlers.match_handler_unit import MatchHandlerUnit


class MatchHandler:
    """
    Class responsible for monitoring all the ongoing matches between 2 players.
    """

    def __init__(self):
        self.units: dict[str, MatchHandlerUnit] = {}

    def initiate_match(self, room_dto: RoomDto):
        """
        Instanciates a match handler unit and its corresponding match for a specific room.

        ⚠️ This function should always be inside of a try except clause, at it may raise an error if a match is already running for a given room ⚠️
        """
        room_id = room_dto.id
        if room_id in self.units:
            raise Exception("")

        match_handler_unit = MatchHandlerUnit(room_dto)

        self.units[room_dto.id] = match_handler_unit
        return match_handler_unit

    def get_unit(self, room_id):
        """
        Gets a unit from the corresponding room id
        """
        try:
            return self.units[room_id]
        except KeyError:
            logger.error(f"No unit currently working for the room : {room_id}")

    def get_match_info(self, room_id):
        """
        Gets the match info for the corresponding room id
        """
        unit = self.get_unit(room_id)

        if not unit:
            return

        return unit.match_info
