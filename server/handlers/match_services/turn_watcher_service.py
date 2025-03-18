from datetime import datetime
from threading import Event
from typing import TYPE_CHECKING, Callable

from config.logging import get_configured_logger
from constants.match_constants import TURN_DURATION_IN_S
from dto.turn_context_dto import TurnContextDto
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
        self._turn_manual_swap_event = Event()
        self._turn_swap_external_callbacks: list[Callable] = []

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
        """Forces a turn swap by raising up the associated threading Event."""
        self._turn_manual_swap_event.set()

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
            self._turn_manual_swap_event.clear()  # Reset the event for the next turn

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
        self.match_context.current_turn += 1
        self.match_context.is_player1_turn = not self.match_context.is_player1_turn

        self._increment_current_player_MP()
        self._enable_spawned_cells()

        self._trigger_external_callbacks()

    def _enable_spawned_cells(self):
        """
        Cells cannot move nor attack on the turn they are spawned, so
        we "wake them up" during the next turn.
        """
        current_player_cells = self.match_context.game_board.get_cells_owned_by_player(
            self.match_context.is_player1_turn,
        )
        for cell in current_player_cells:
            if cell.is_freshly_spawned():
                cell.clear_core_state()

    def _increment_current_player_MP(self):
        """
        Increments the current player's available mana points for the turn by 1.
        """
        current_turn = self.match_context.current_turn
        current_player = self.match.get_current_player()

        player_game_info = current_player.resources

        remainder = current_turn % 2
        quotient = current_turn // 2

        player_game_info.current_mp = min(quotient + remainder, player_game_info.max_mp)

    def _trigger_external_callbacks(self):
        for callback in self._turn_swap_external_callbacks:
            callback()
