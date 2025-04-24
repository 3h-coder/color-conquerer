from threading import Event
from typing import TYPE_CHECKING

from flask import copy_current_request_context, request
from flask_socketio import SocketIO

from config.logging import get_configured_logger
from constants.match_constants import DELAY_IN_S_BEFORE_MATCH_EXCLUSION
from dto.server_only.match_closure_dto import EndingReason
from handlers.match_services.service_base import ServiceBase
from utils import session_utils

if TYPE_CHECKING:
    from handlers.match_handler_unit import MatchHandlerUnit


class PlayerExitWatcherService(ServiceBase):
    """
    Helper class responsible for watching player exits, and triggering and match
    ending if a player leaves and does not come back before the exit timeout.
    """

    def __init__(self, match_handler_unit: "MatchHandlerUnit"):
        super().__init__(match_handler_unit)
        self._logger = get_configured_logger(__name__)

        self._exit_delay_in_s = DELAY_IN_S_BEFORE_MATCH_EXCLUSION

        # Events used to cancel an exit watcher task for a specific player, i.e. not kick the player out when they reconnect
        self.player_exit_watch_stop_events = {
            self.match_context.player1.player_id: Event(),
            self.match_context.player2.player_id: Event(),
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
            self._logger.debug(
                f"({request.remote_addr}) | Starting the exit watch for the player {player_id}"
            )

            if stop_event.wait(timeout=self._exit_delay_in_s):
                self._logger.debug(
                    f"({request.remote_addr}) | The exit watch was stopped"
                )
            else:
                if not self.match.is_ended():
                    self.match.end(EndingReason.PLAYER_LEFT, loser_id=player_id)
                session_utils.clear_match_info()

        self._server.socketio.start_background_task(target=exit_timer)
