from datetime import datetime
from threading import Event
from typing import TYPE_CHECKING, Callable

from config.logging import get_configured_logger
from constants.match_constants import TURN_DURATION_IN_S
from game_engine.turn_change_processing import process_turn_change
from handlers.match_services.client_notifications import notify_turn_swap
from handlers.match_services.service_base import ServiceBase

if TYPE_CHECKING:
    from handlers.match_handler_unit import MatchHandlerUnit


class TurnWatcherService(ServiceBase):
    """
    Helper class responsible of properly managing turn swapping and all of the associated events.
    """

    def __init__(self, match_handler_unit: "MatchHandlerUnit"):
        super().__init__(match_handler_unit)
        self._logger = get_configured_logger(__name__)

        self._turn_start_time: datetime = None
        self._turn_watcher_thread = None
        self._turn_swap_request_event = Event()
        self._turn_swap_external_callbacks: list[Callable] = []

        self.turn_swap_complete_event = Event()
        self.turn_duration_in_s = TURN_DURATION_IN_S

    def add_external_callback(self, callback: Callable):
        self._turn_swap_external_callbacks.append(callback)

    def trigger(self):
        """
        Triggers the background task that will handle turn swapping.
        """

        def watch_turns():
            while not self.match.is_ended():
                self._turn_start_time = datetime.now()

                # Wait for the turn duration or a manual end signal
                if not self._turn_swap_request_event.wait(
                    timeout=self.turn_duration_in_s
                ):
                    # Timeout: Automatically end the turn
                    self._swap_turn(manual=False)
                else:
                    # Manual turn end signal received
                    self._swap_turn(manual=True)

        self._turn_watcher_thread = self._server.socketio.start_background_task(
            target=watch_turns
        )

    def force_turn_swap(self):
        """Forces a turn swap by raising up the associated threading Event."""
        self._turn_swap_request_event.set()

    def get_remaining_turn_time(self):
        """Returns the remining time in seconds for the current turn."""
        elapsed_time = datetime.now() - self._turn_start_time
        return max(0, TURN_DURATION_IN_S - elapsed_time.seconds)

    def _swap_turn(self, manual=False):
        """
        Handles the logic to end the current turn and transition to the next.
        """
        if self.match.is_ended():
            return

        if manual:
            self._turn_swap_request_event.clear()  # Reset the event for the next turn

        self._process_turn_swap()

        player1_room, player2_room = self.match.get_individual_player_rooms()
        # Notify the turn change to players
        notify_turn_swap(
            self.match.get_turn_context_dto(for_player1=True, for_new_turn=True),
            self.match.get_turn_context_dto(for_player1=False, for_new_turn=True),
            player1_room,
            player2_room,
            self.match.lock,
        )

    def _process_turn_swap(self):
        """
        Performs all the processing related to turn swapping such as
        incrementing the turn or adding a mana point to the player whose turn it will be.
        """
        process_turn_change(self.match_context)
        self._trigger_external_callbacks()
        self.turn_swap_complete_event.set()  # Signal that the turn swap is complete
        self.turn_swap_complete_event.clear()  # Reset for the next turn

    def _trigger_external_callbacks(self):
        for callback in self._turn_swap_external_callbacks:
            callback()
