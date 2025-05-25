from typing import Callable

from config import config
from config.logging import get_configured_logger
from config.variables import RequiredVariable
from dto.player.queue_player_dto import QueuePlayerDto
from game_engine.models.dtos.room import Room
from utils.id_generation_utils import generate_id


class RoomHandler:
    """
    Class responsible for creating the player rooms from which
    matches will be created.
    """

    def __init__(self):
        self.logger = get_configured_logger(__name__)
        self.open_rooms: dict[str, Room] = {}
        self.closed_rooms: dict[str, Room] = {}
        self.MAX_CLOSED_ROOMS = config.get(RequiredVariable.GAME_MAX_ROOM_CAPACITY)

    def at_capacity(self):
        """
        Indicates whether or not the room handler has reached its closed rooms limit
        """
        return len(self.closed_rooms) >= self.MAX_CLOSED_ROOMS

    def room_exists(self, room_id):
        return room_id in self.open_rooms or room_id in self.closed_rooms

    def make_enter_in_room(
        self, player_register_dto: QueuePlayerDto
    ) -> tuple[Room, bool]:
        """
        Makes the player enter an either open or closed room.

        Returns :
            A tuple with the room id and a boolean indicating whether or not the room is closed.
        """

        # Note : Currently there can only be one open room that gets freed immediately once
        # a second player enters it. In the future we may have multiple open rooms at once
        # to implement match making algorithms.
        if not self.open_rooms:
            room_id = generate_id(Room)
            new_room = Room(
                id=room_id,
                player1_queue_dto=player_register_dto,
                player2_queue_dto=None,
                player1_room_id=f"{room_id}-p1",
                player2_room_id=f"{room_id}-p2",
                session_ids={},
            )
            self.open_rooms[new_room.id] = new_room
            self._log_rooms_count()
            return new_room, False

        # Place the player in the first open room
        room = self.open_rooms[next(iter(self.open_rooms))]
        room.player2_queue_dto = player_register_dto

        self._transfer_open_room_to_closed_rooms(room)

        return room, True

    def remove_open_room(self, room_id: str):
        if room_id not in self.open_rooms:
            return

        self.logger.info(f"Removing the open room {room_id}")
        del self.open_rooms[room_id]
        self._log_rooms_count()

    def remove_closed_room(self, room_id: str):
        if room_id not in self.closed_rooms:
            return

        self.logger.info(f"Removing the closed room {room_id}")
        del self.closed_rooms[room_id]
        self._log_rooms_count()

    def _transfer_open_room_to_closed_rooms(self, room: Room):
        """
        Transfers a room from the open rooms to the closed rooms, triggering the
        transfer callback
        """
        self.closed_rooms[room.id] = room
        self.remove_open_room(room.id)

    def _log_rooms(self):
        self.logger.debug(f"Open rooms {self.open_rooms}")
        self.logger.debug(f"Closed rooms {self.closed_rooms}")

    def _log_rooms_count(self):
        self.logger.info(f"Open rooms count : {len(self.open_rooms)}")
        self.logger.info(f"Closed rooms count : {len(self.closed_rooms)}")
