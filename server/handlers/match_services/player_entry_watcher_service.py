from typing import TYPE_CHECKING

from flask import copy_current_request_context

from constants.match_constants import DELAY_IN_S_TO_WAIT_FOR_EVERYONE
from game_engine.models.match.cancellation_reason import CancellationReason
from handlers.match_services.service_base import ServiceBase

if TYPE_CHECKING:
    from handlers.match_handler_unit import MatchHandlerUnit


class PlayerEntryWatcherService(ServiceBase):
    """
    Helper class responsible for checking if players manage to be ready
    in time, and prematurely cancelling or ending the match if necessary.

    Clients send the ready signal after they arrive in the play room and
    successfully fetch the match and player context information.
    """

    def __init__(self, match_handler_unit: "MatchHandlerUnit"):
        super().__init__(match_handler_unit)
        self._logger = match_handler_unit.logger

        # Dictionary used to determine which player is ready or not
        self._players_ready = {
            self.match_context.player1.player_id: False,
            self.match_context.player2.player_id: False,
        }

    def mark_player_as_ready(self, player_id):
        if not player_id in self._players_ready:
            self._logger.error(
                f"Cannot mark the player {player_id} as ready as it is not present in the dictionary."
            )
            return

        self._players_ready[player_id] = True

    def all_players_ready(self):
        """
        Returns True if all the players are marked as ready, False otherwise.
        """
        return all(value is True for value in self._players_ready.values())

    def watch_player_entry(self):
        """
        Waits a specific delay before prematurely ending or cancelling the match
        if at least one player did not join.
        """

        @copy_current_request_context
        def prematurely_end_or_cancel_match_if_necessary():
            self._server.socketio.sleep(DELAY_IN_S_TO_WAIT_FOR_EVERYONE)

            # The match started successfully, do nothing
            if self.match.is_ongoing():
                return

            # No player could make it in time, so cancel the match
            if self._no_player_joined():
                self._logger.info("No player joined the match")
                self.match.cancel(
                    cancellation_reason=CancellationReason.BOTH_PLAYERS_NEVER_JOINED
                )
                return

            # One of the players could not make it in time, the other gets notified about the cancellation
            for player_id in self._players_ready:
                if not self._players_ready[player_id]:
                    self.match.cancel(
                        cancellation_reason=CancellationReason.PLAYER_NEVER_JOINED,
                        penalized_player_id=player_id,
                    )

        self._server.socketio.start_background_task(
            target=prematurely_end_or_cancel_match_if_necessary
        )

    def _no_player_joined(self):
        """
        Returns True if none the players are marked as ready, False otherwise.
        """
        return all(value is False for value in self._players_ready.values())
