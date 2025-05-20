from typing import TYPE_CHECKING

from config.logging import get_configured_logger
from events.events import Events
from events.shared_notifications import match_launch_error_redirect
from game_engine.models.dtos.room import Room
from game_engine.models.match.cancellation_reason import CancellationReason
from handlers.match_handler_unit import MatchHandlerUnit

if TYPE_CHECKING:
    from server import Server


class MatchHandler:
    """
    Class responsible for monitoring all the pending and ongoing matches between 2 players.
    """

    def __init__(self, server: "Server"):
        self.logger = get_configured_logger(__name__)
        self.units: dict[str, MatchHandlerUnit] = {}
        self._server = server
        self._sleep_duration_in_s_after_opponent_found = 1

    def notify_clients_and_initiate_match(self, room: Room):
        """
        Notifies the client that an opponent has been found, and
        initiate the match.
        """
        server = self._server
        room_id = room.id
        server.socketio.emit(Events.SERVER_QUEUE_OPPONENT_FOUND, to=room_id)

        # Note : This leaves the time for the second client to actually save the player info and room_id into
        # the session (often fails with instant redirects)
        server.socketio.sleep(self._sleep_duration_in_s_after_opponent_found)

        # Order the client to go to the match room, and launch the match
        server.socketio.emit(Events.SERVER_GO_TO_MATCH_ROOM, to=room_id)
        self._initiate_match_for_room(room)

    def get_unit(self, room_id: str):
        """
        Gets a unit from the corresponding room id
        """
        try:
            return self.units[room_id]
        except KeyError:
            self.logger.error(f"No unit instanciated for the room : {room_id}")

    def get_match_context(self, room_id):
        """
        Gets the match info for the corresponding room id
        """
        unit = self.get_unit(room_id)

        if not unit:
            return None

        return unit.match_context

    def _initiate_match_for_room(self, room: Room):
        try:
            match = self._create_match_handler_unit(room)
            match.watch_player_entry()
        except Exception:
            self.logger.exception(f"An error occured when trying to launch a match")
            if match is not None:
                match.cancel(cancellation_reason=CancellationReason.SERVER_ERROR)

            match_launch_error_redirect(broadcast_to=room.id)

    def _create_match_handler_unit(self, room: Room):
        """
        Instanciates a match handler unit and its corresponding match for a specific room.
        """
        self.logger.info(f"Creating a match handler unit for the room {room.id}")
        room_id = room.id
        if room_id in self.units:
            error_msg = f"The room {room_id} already has an attributed unit"
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        match_handler_unit = MatchHandlerUnit(room)

        self.units[room.id] = match_handler_unit
        return match_handler_unit
