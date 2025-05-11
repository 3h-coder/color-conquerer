from typing import TYPE_CHECKING

from config.logging import get_configured_logger
from constants.match_constants import COUNTDOWN_BEFORE_START_IN_S
from events.shared_notifications import match_launch_error_redirect
from game_engine.models.match.cancellation_reason import CancellationReason
from handlers.match_services.client_notifications import (
    notify_countdown,
    notify_match_start,
)
from handlers.match_services.service_base import ServiceBase

if TYPE_CHECKING:
    from handlers.match_handler_unit import MatchHandlerUnit


class MatchStartService(ServiceBase):
    """
    Helper class to initiate a countdown and actually start a match.
    """

    def __init__(self, match_handler_unit: "MatchHandlerUnit"):
        super().__init__(match_handler_unit)
        self._logger = match_handler_unit.logger

    def countdown_and_start(self):
        """
        Triggers a 5 seconds
        """
        count = COUNTDOWN_BEFORE_START_IN_S
        self._notify_match_start(pre_countdown=True)
        self.match.server.socketio.sleep(0.5)
        while count > 0:
            notify_countdown(room_id=self.room_id, count=count)
            count -= 1
            self.match.server.socketio.sleep(1)
        self.start()

    def start(self):
        """
        Starts the match, setting up the turn watcher and notifying the clients.
        """
        try:
            self._logger.info(
                f"Match start requested for the match in the room {self.match_context.room_id}"
            )

            if not self.match.is_waiting_to_start():
                self._logger.warning(
                    f"Can only start a match that is waiting to start. The match status is {self.match.status.name}"
                )
                return

            self._logger.info(
                f"Starting the match in the room {self.match_context.room_id}"
            )

            # Important variables set up
            self.match_context.current_turn = 1
            self.match_context.is_player1_turn = True
            self.match.turn_state.is_player1_turn = True

            # Trigger the turn watcher service to process player turns
            self.match._turn_watcher_service.trigger()
            # Trigger the inactivity watcher service to watch for inactive players
            self.match._player_inactivity_watcher_service.trigger()

            # notify the clients
            self._notify_match_start(pre_countdown=False)

            # IMPORTANT : This must be set at the end otherwise cancellation will be denied
            # as only a match with the WAITING_TO_START status can be cancelled
            self.match.mark_as_ongoing()
        except Exception:
            self._logger.exception(f"Failed to start the match")
            self.match.cancel(cancellation_reason=CancellationReason.SERVER_ERROR)

            match_launch_error_redirect(
                broadcast_to=self.match_context.room_id,
            )

    def _notify_match_start(self, pre_countdown: bool):
        notify_match_start(
            self.match.get_turn_context_dto(
                for_player1=True,
                for_new_turn=not pre_countdown,
                pre_match_start=pre_countdown,
            ),
            self.match.get_turn_context_dto(
                for_player1=False,
                for_new_turn=not pre_countdown,
                pre_match_start=pre_countdown,
            ),
            self.match_context.player1.individual_room_id,
            self.match_context.player2.individual_room_id,
            self.match.lock,
        )
