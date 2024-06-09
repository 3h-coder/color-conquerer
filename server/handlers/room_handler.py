import uuid

from config.logger import logger
from dto.room_dto import RoomDto


class RoomHandler:
    """
    Class responsible for handling a room of 2 players
    during a match.
    """

    def __init__(self):
        self.open_rooms: list[RoomDto] = []
        self.closed_rooms: list[RoomDto] = []

    def make_enter_in_room(self, playerId: str):
        if not self.open_rooms:
            new_room = RoomDto(
                id=f"room-{uuid.uuid4()}", player1id=playerId, player2id=None
            )
            self.open_rooms.append(new_room)
            logger.debug(f"Open rooms {self.open_rooms}")
            return new_room.id

        # Place the player in the first open room
        room = self.open_rooms[0]
        room.player2id = playerId
        # Move the room to the closed rooms
        self.closed_rooms.append(room)
        self.open_rooms.pop(0)

        logger.debug(f"Closed rooms {self.closed_rooms}")

        return room.id
