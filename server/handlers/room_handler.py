import uuid

from config.logger import logger
from dto.room_dto import RoomDto


class RoomHandler:
    """
    Class responsible for handling a room of 2 players
    during a match.
    """

    def __init__(self):
        self.open_rooms: dict[str, RoomDto] = {}
        self.closed_rooms: dict[str, RoomDto] = {}

    def make_enter_in_room(self, player_id: str):
        if not self.open_rooms:
            new_room = RoomDto(
                id=f"room-{uuid.uuid4()}", player1id=player_id, player2id=None
            )
            self.open_rooms[new_room.id] = new_room
            self._log_rooms()
            return new_room.id, False

        # Place the player in the first open room
        room = self.open_rooms[next(iter(self.open_rooms))]
        room.player2id = player_id
        # Move the room to the closed rooms
        self.closed_rooms[room.id] = room
        del self.open_rooms[room.id]

        self._log_rooms()

        return room.id, True

    def remove_room(self, room_id: str):
        del self.open_rooms[room_id]

        self._log_rooms()

    def _log_rooms(self):
        logger.debug(f"Open rooms {self.open_rooms}")
        logger.debug(f"Closed rooms {self.closed_rooms}")
