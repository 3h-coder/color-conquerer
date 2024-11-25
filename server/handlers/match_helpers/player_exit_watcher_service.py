from threading import Event
from typing import TYPE_CHECKING

from flask import copy_current_request_context, request
from flask_socketio import SocketIO

from constants.match_constants import DELAY_IN_S_BEFORE_MATCH_EXCLUSION
from dto.server_only.match_closure_dto import EndingReason
from handlers.match_helpers.service_base import ServiceBase
from utils import session_utils

if TYPE_CHECKING:
    from handlers.match_helpers.match_handler_unit import MatchHandlerUnit


class PlayerExitWatcherService(ServiceBase):
    """
    Helper class responsible for watching player exits, and triggering and match
    ending if a player leaves and does not come back before the exit timeout.
    """

    def __init__(self, match_handler_unit: "MatchHandlerUnit"):
        super().__init__(match_handler_unit)

        # Events used to cancel an exit watcher task for a specific player, i.e. not kick the player out when they reconnect
        self.player_exit_watch_stop_events = {
            self.match_info.player1.playerId: Event(),
            self.match_info.player2.playerId: Event(),
        }

    def stop_watching_player_exit(self, player_id: str):
        """
        Sets the exit watcher stop event for the given player.
        """
        self.player_exit_watch_stop_events[player_id].set()

    def watch_player_exit(self, player_id: str):
        """
        Watches a player exit, ending the match after a given delay unless the
        exit watcher stop event for the player is set.
        """
        stop_event = self.player_exit_watch_stop_events[player_id]
        stop_event.clear()

        @copy_current_request_context
        def exit_timer():
            self.logger.debug(
                f"({request.remote_addr}) | Starting the exit watch for the player {player_id}"
            )
            self._polling_sleep(
                self._server.socketio, DELAY_IN_S_BEFORE_MATCH_EXCLUSION, stop_event
            )

            if stop_event.is_set():
                self.logger.debug(
                    f"({request.remote_addr}) | The exit watch was stopped"
                )
                return

            self.match.end(EndingReason.PLAYER_LEFT, loser_id=player_id)
            session_utils.clear_match_info()

        self._server.socketio.start_background_task(target=exit_timer)

    def _polling_sleep(
        self, socketio: SocketIO, sleep_duration_in_s: int, stop_event: Event
    ):
        check_interval_in_s = 0.05  # 50 ms
        elapsed = 0

        while elapsed < sleep_duration_in_s:
            if stop_event.is_set():
                return
            socketio.sleep(check_interval_in_s)
            elapsed += check_interval_in_s
