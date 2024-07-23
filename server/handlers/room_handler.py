import uuid

from config.logger import logger
from dto.queue_player_dto import QueuePlayerDto
from dto.room_dto import RoomDto
from helpers.id_generation_helper import generate_id


class RoomHandler:
    """
    Class responsible for handling a room of 2 players
    during a match.
    """

    # TODO: Make this variable configurable
    MAX_CLOSED_ROOMS = 50

    def __init__(self):
        self.open_rooms: dict[str, RoomDto] = {}
        self.closed_rooms: dict[str, RoomDto] = {}

    def at_capacity(self):
        """
        Indicates whether or not the room handler has reached its closed rooms limit
        """
        return len(self.closed_rooms) == self.MAX_CLOSED_ROOMS

    def make_enter_in_room(self, player_register_dto: QueuePlayerDto):
        """
        Makes the player enter an either open or closed room.

        Returns :
            A tuple with the room id and a boolean indicating whether or not the room is closed.
        """
        if not self.open_rooms:
            new_room = RoomDto(
                id=generate_id(RoomDto), player1=player_register_dto, player2=None
            )
            self.open_rooms[new_room.id] = new_room
            self._log_rooms_count()
            return new_room.id, False

        # Place the player in the first open room
        room = self.open_rooms[next(iter(self.open_rooms))]
        room.player2 = player_register_dto

        # Move the room to the closed rooms
        self.closed_rooms[room.id] = room
        self.remove_room(room.id)

        return room.id, True

    def remove_room(self, room_id: str):
        logger.debug(f"Removing the room {room_id}")
        del self.open_rooms[room_id]
        self._log_rooms_count()

    def _log_rooms(self):
        logger.debug(f"Open rooms {self.open_rooms}")
        logger.debug(f"Closed rooms {self.closed_rooms}")

    def _log_rooms_count(self):
        logger.debug(f"Open rooms count : {len(self.open_rooms)}")
        logger.debug(f"Closed rooms count : {len(self.closed_rooms)}")
