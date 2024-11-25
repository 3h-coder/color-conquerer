from datetime import datetime
from threading import Event
from typing import TYPE_CHECKING

from config.logging import get_configured_logger
from constants.match_constants import TURN_DURATION_IN_S
from dto.turn_info_dto import TurnInfoDto
from handlers.match_helpers.client_notifications import notify_turn_swap

if TYPE_CHECKING:
    from handlers.match_helpers.match_handler_unit import MatchHandlerUnit
    from server import Server


class TurnWatcherService:
    """
    Helper class to properly manage turn swapping and all of the associated events.
    """

    def __init__(self, server_ref: "Server", match_handler_unit: "MatchHandlerUnit"):
        self.logger = get_configured_logger(__name__)
        self._server = server_ref
        self.match = match_handler_unit
        self.match_info = match_handler_unit.match_info

        self._turn_start_time: datetime = None
        self._turn_watcher_thread = None
        self._turn_manual_swap_event = Event()

    def trigger(self):
        """
        Triggers the background task that will handle turn swaping.
        """

        def watch_turns():
            while not self.match.is_ended():
                self._turn_start_time = datetime.now()

                # Wait for the turn duration or a manual end signal
                if not self._turn_manual_swap_event.wait(timeout=TURN_DURATION_IN_S):
                    # Timeout: Automatically end the turn
                    self._swap_turn(manual=False)
                else:
                    # Manual turn end signal received
                    self._swap_turn(manual=True)

        self._turn_watcher_thread = self._server.socketio.start_background_task(
            target=watch_turns
        )

    def force_turn_swap(self):
        """Forces a turn swap by raising up the associated threading Event"""
        self._turn_manual_swap_event.set()

    def get_remaining_turn_time(self):
        """Returns the remining time in seconds for the current turn"""
        elapsed_time = datetime.now() - self._turn_start_time
        return max(0, TURN_DURATION_IN_S - elapsed_time.seconds)

    def _swap_turn(self, manual=False):
        """
        Handles the logic to end the current turn and transition to the next.
        """
        if self.match.is_ended():
            return

        if manual:
            self._turn_manual_swap_event.clear()  # Reset the event for the next turn

        # Increment the turn count
        self.match_info.currentTurn += 1
        # Swap the current player's turn
        self.match_info.isPlayer1Turn = not self.match_info.isPlayer1Turn

        # Notify the turn change to players
        notify_turn_swap(
            TurnInfoDto(
                self.match.get_current_player_id(),
                self.match_info.isPlayer1Turn,
                TURN_DURATION_IN_S,
                notifyTurnChange=True,
            ),
            self.match_info.roomId,
        )
