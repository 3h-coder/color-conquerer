from threading import Event
from typing import TYPE_CHECKING

from constants.match_constants import DELAY_IN_S_TO_WAIT_FOR_EVERYONE
from dto.server_only.match_closure_dto import EndingReason
from handlers.match_helpers.service_base import ServiceBase

if TYPE_CHECKING:
    from handlers.match_helpers.match_handler_unit import MatchHandlerUnit


class PlayerEntryWatcherService(ServiceBase):
    """
    Helper class responsible for checking if players manage to be ready
    in time, and prematurely cancelling or ending the match if necessary.

    Clients send the ready signal after they arrive in the play room and
    successfully fetch the match and player context information.
    """

    def __init__(self, match_handler_unit: "MatchHandlerUnit"):
        super().__init__(match_handler_unit)

        # Dictionary used to determine which player is ready or not
        self._players_ready = {
            self.match_info.player1.playerId: False,
            self.match_info.player2.playerId: False,
        }

    def mark_player_as_ready(self, player_id):
        if not player_id in self._players_ready:
            self.logger.error(
                f"Cannot mark the player {player_id} as ready as it does it not in the dictionary."
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

        def prematurely_end_or_cancel_match_if_necessary():
            self._server.socketio.sleep(DELAY_IN_S_TO_WAIT_FOR_EVERYONE)

            # The match started successfully, do nothing
            if self.match.is_ongoing():
                return

            # No player could make it in time, so cancel the match
            if self._no_player_joined():
                self.logger.info("No player joined the match")
                self.match.cancel()
                return

            # One of the players could not make it in time, the other automatically wins
            for player_id in self._players_ready:
                if not self._players_ready[player_id]:
                    self.match.end(EndingReason.NEVER_JOINED, loser_id=player_id)

        self._server.socketio.start_background_task(
            target=prematurely_end_or_cancel_match_if_necessary
        )

    def _no_player_joined(self):
        """
        Returns True if none the players are marked as ready, False otherwise.
        """
        return all(value is False for value in self._players_ready.values())
