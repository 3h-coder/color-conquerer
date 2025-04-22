from datetime import datetime
from threading import Event
from config.logging import get_configured_logger
from constants.match_constants import (
    INACTIVITY_FINAL_WARNING_DELAY_IN_S,
    INACTIVITY_FIRST_WARNING_DELAY_IN_S,
    INACTIVITY_KICK_DELAY_IN_S,
)
from dto.server_only.match_closure_dto import EndingReason
from handlers.match_services.client_notifications import notify_inactivity_warning
from handlers.match_services.service_base import ServiceBase

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from handlers.match_handler_unit import MatchHandlerUnit


class PlayerInactivityWatcherService(ServiceBase):
    """
    Helper class responsible for watching player inactivity.
    A player is considered inactive when they do not perform any action (i.e
    cell movement, spawn, attack or spell casting) within a certain amount of time while
    it is their turn.
    """

    def __init__(self, match_handler_unit: "MatchHandlerUnit"):
        super().__init__(match_handler_unit)
        self._logger = get_configured_logger(__name__)

        self._watching_player1: bool = True

        self._first_warning_delay_in_s = INACTIVITY_FIRST_WARNING_DELAY_IN_S
        self._final_warning_delay_in_s = INACTIVITY_FINAL_WARNING_DELAY_IN_S
        self._kick_delay_in_s = INACTIVITY_KICK_DELAY_IN_S

        self._player1_events = PlayerInactivityWatcherEventsBundle(for_player1=True)
        self._player2_events = PlayerInactivityWatcherEventsBundle(for_player1=False)
        self._current_player_events = self._player1_events

    def trigger(self):
        """
        Starts background threads to notify inactivity warnings for both players.
        """
        self._launch_watchers()

    def report_activity(self):
        """
        Resets the inactivity events bound to the player whose activity got reported,
        and watches for inactivity again.
        """
        self._current_player_events.reset()
        self._launch_watchers()

    def on_turn_swap(self):
        """
        Stops the inactivity watcher for the current player and resumes them for the player
        whose turn it is now.
        """
        self._current_player_events.freeze()

        self._watching_player1 = not self._watching_player1
        self._current_player_events = (
            self._player1_events if self._watching_player1 else self._player2_events
        )

        self._launch_or_resume_watchers()

    def _launch_or_resume_watchers(self):
        player_events = self._current_player_events
        if player_events.freeze_time is None:
            self._launch_watchers()
        else:
            elapsed_time_in_s = (
                player_events.freeze_time - player_events.launch_time
            ).total_seconds()
            self._resume_watchers(elapsed_time_in_s)

    def _resume_watchers(self, elapsed_time_in_s: float):
        first_warning_remaining_delay_in_s: float | None = None
        final_warning_remaining_delay_in_s: float | None = None

        if elapsed_time_in_s < self._first_warning_delay_in_s:
            first_warning_remaining_delay_in_s = (
                self._first_warning_delay_in_s - elapsed_time_in_s
            )

        if elapsed_time_in_s < self._final_warning_delay_in_s:
            final_warning_remaining_delay_in_s = (
                self._final_warning_delay_in_s - elapsed_time_in_s
            )

        # The elapsed timed has to be lower than the kick delay, otherwise the match would have already
        # been ended
        player_kick_remaining_delay_in_s = self._kick_delay_in_s - elapsed_time_in_s

        # Relaunch the watchers with the updated delays
        self._current_player_events.launch_time = datetime.now()
        if first_warning_remaining_delay_in_s is not None:
            self._launch_first_inactivity_warning_watcher(
                first_warning_remaining_delay_in_s
            )
        if final_warning_remaining_delay_in_s is not None:
            self._launch_final_inactivity_warning_watcher(
                final_warning_remaining_delay_in_s
            )
        self._launch_player_kick_watcher(player_kick_remaining_delay_in_s)

    def _launch_watchers(self):
        self._current_player_events.launch_time = datetime.now()

        self._launch_first_inactivity_warning_watcher()
        self._launch_final_inactivity_warning_watcher()
        self._launch_player_kick_watcher()

    def _launch_first_inactivity_warning_watcher(self, delay_in_s: int | float = None):
        if delay_in_s is None:
            delay_in_s = self._first_warning_delay_in_s

        self._server.socketio.start_background_task(
            target=self._notify_inactivity_warning,
            for_player1=self._current_player_events.for_player1,
            inactivity_warning_event=self._current_player_events.first_warning_event,
            delay_in_s=delay_in_s,
        )

    def _launch_final_inactivity_warning_watcher(self, delay_in_s: int | float = None):
        if delay_in_s is None:
            delay_in_s = self._final_warning_delay_in_s

        self._server.socketio.start_background_task(
            target=self._notify_inactivity_warning,
            for_player1=self._current_player_events.for_player1,
            inactivity_warning_event=self._current_player_events.final_warning_event,
            delay_in_s=delay_in_s,
        )

    def _launch_player_kick_watcher(self, delay_in_s: int | float = None):
        if delay_in_s is None:
            delay_in_s = self._kick_delay_in_s

        self._server.socketio.start_background_task(
            target=self._kick_player_out_and_end_the_match,
            loser_id=self.match.get_current_player().player_id,
            kick_event=self._current_player_events.inactivity_kick_event,
            delay_in_s=delay_in_s,
        )

    def _notify_inactivity_warning(
        self, for_player1: bool, inactivity_warning_event: Event, delay_in_s: int
    ):
        """
        Waits for the specified delay and triggers the inactivity warning notification.
        """
        if not inactivity_warning_event.wait(timeout=delay_in_s):
            player_room = (
                self.match.get_individual_player_rooms()[0]
                if for_player1
                else self.match.get_individual_player_rooms()[1]
            )
            notify_inactivity_warning(player_room)

    def _kick_player_out_and_end_the_match(
        self, loser_id: str, kick_event: Event, delay_in_s: int
    ):
        if not kick_event.wait(timeout=delay_in_s):
            if self.match.is_ended():
                return
            self.match.end(EndingReason.PLAYER_INACTIVE, loser_id=loser_id)


class PlayerInactivityWatcherEventsBundle:
    """
    Class used to store the events related to the player's inactivity observation.
    """

    def __init__(self, for_player1: bool):
        self.for_player1 = for_player1
        self.first_warning_event = Event()
        self.final_warning_event = Event()
        self.inactivity_kick_event = Event()
        # Time at which we start watching for player inactivity
        self.launch_time: datetime | None = None
        # Time at which we stop watching for player inactivity
        self.freeze_time: datetime | None = None

    def reset(self):
        self._set_all()
        self._clear_all()

    def freeze(self):
        self.freeze_time = datetime.now()
        self.reset()

    def _set_all(self):
        self.first_warning_event.set()
        self.final_warning_event.set()
        self.inactivity_kick_event.set()

    def _clear_all(self):
        self.first_warning_event.clear()
        self.final_warning_event.clear()
        self.inactivity_kick_event.clear()
