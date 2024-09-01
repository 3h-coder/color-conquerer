from config.logger import logger
from constants.match_constants import DELAY_IN_S_BEFORE_MATCH_EXCLUSION
from dto.room_dto import RoomDto
from handlers.match_handler_unit import MatchHandlerUnit


class MatchHandler:
    """
    Class responsible for monitoring all the pending and ongoing matches between 2 players.
    """

    def __init__(self):
        self.units: dict[str, MatchHandlerUnit] = {}

    def initiate_match(self, room_dto: RoomDto):
        """
        Instanciates a match handler unit and its corresponding match for a specific room.
        """
        room_id = room_dto.id
        if room_id in self.units:
            raise ValueError(f"The room {room_id} already has an attributed unit")

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
            logger.error(f"No unit instanciated for the room : {room_id}")

    def get_match_info(self, room_id):
        """
        Gets the match info for the corresponding room id
        """
        unit = self.get_unit(room_id)

        if not unit:
            return

        return unit.match_info
