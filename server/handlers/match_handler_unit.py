from enum import Enum

from config.logging import get_configured_logger
from constants.match_constants import TURN_DURATION_IN_S
from dto.player_resources_bundle_dto import PlayerResourceBundleDto
from dto.server_only.match_closure_dto import EndingReason
from dto.turn_context_dto import TurnContextDto
from game_engine.models.match_context import MatchContext
from game_engine.models.room import Room
from game_engine.models.turn_state import TurnState
from handlers.match_services.client_notifications import notify_match_start
from handlers.match_services.match_actions_service import MatchActionsService
from handlers.match_services.match_termination_service import MatchTerminationService
from handlers.match_services.player_entry_watcher_service import (
    PlayerEntryWatcherService,
)
from handlers.match_services.player_exit_watcher_service import PlayerExitWatcherService
from handlers.match_services.turn_watcher_service import TurnWatcherService
from server_gate import get_server
from utils.id_generation_utils import generate_id


class MatchHandlerUnit:
    """
    Handles a single ongoing match.
    Manages the whole lifecyle (start to end) partly thanks to underlying helper classes instances.
    """

    def __init__(self, room: Room):
        self.logger = get_configured_logger(__name__)
        self.server = get_server()

        self.match_context: MatchContext = self._get_initial_match_context(room)
        player1 = self.match_context.player1
        player2 = self.match_context.player2
        self.turn_state: TurnState = TurnState.get_initial(
            player1_turn=False,
            player1_resources=player1.resources,
            player2_resources=player2.resources,
        )

        self.status = MatchStatus.WAITING_TO_START

        self._match_termination_service = MatchTerminationService(self)

        self._match_actions_service = MatchActionsService(self)

        self._player_entry_watcher_service = PlayerEntryWatcherService(self)

        self._player_exit_watcher_service = PlayerExitWatcherService(self)

        self._turn_watcher_service = TurnWatcherService(self)
        self._turn_watcher_service.add_external_callback(
            self._match_actions_service.reset_for_new_turn
        )

    def is_waiting_to_start(self):
        return self.status == MatchStatus.WAITING_TO_START

    def is_ongoing(self):
        return self.status == MatchStatus.ONGOING

    def is_ended(self):
        return self.status == MatchStatus.ENDED

    def is_cancelled(self):
        return self.status == MatchStatus.ABORTED

    def mark_as_ended(self):
        """
        WARNING : To only be used in the match termination service.

        Allows it not to import MatchStatus.
        """
        self.status = MatchStatus.ENDED

    def mark_as_cancelled(self):
        """
        WARNING : To only be used in the match termination service.

        Allows it not to import MatchStatus.
        """
        self.status = MatchStatus.ABORTED

    def watch_player_entry(self):
        """
        Waits a specific delay before prematurely ending or cancelling the match
        if at least one player did not join.
        """
        self._player_entry_watcher_service.watch_player_entry()

    def mark_player_as_ready(self, player_id):
        self._player_entry_watcher_service.mark_player_as_ready(player_id)

    def all_players_ready(self):
        """
        Returns True if all the players are marked as ready, False otherwise.
        """
        return self._player_entry_watcher_service.all_players_ready()

    def start(self):
        """
        Starts the match, setting up the turn watcher and notifying the clients.
        """
        self.logger.info(
            f"Match start requested for the match in the room {self.match_context.room_id}"
        )

        if not self.is_waiting_to_start():
            self.logger.warning(
                f"Can only start a match that is waiting to start. The match status is {self.status.name}"
            )
            return

        self.logger.info(f"Starting the match in the room {self.match_context.room_id}")

        self.status = MatchStatus.ONGOING
        self.match_context.current_turn = 1
        self.match_context.is_player1_turn = True
        self.turn_state.is_player1_turn = True

        # Trigger the turn watcher service to process player turns
        self._turn_watcher_service.trigger()

        # notify the clients
        notify_match_start(
            self.get_turn_context_dto(for_new_turn=True),
            self.match_context.room_id,
        )

    def cancel(self):
        self._match_termination_service.cancel_match()

    def end(
        self,
        reason: EndingReason,
        winner_id: str | None = None,
        loser_id: str | None = None,
    ):
        """
        Declares the match as ended, registering the information in a
        dedicated database and removing the room from the room handler.

        Additionally, notifies all players and schedules this match handler unit's garbage collection.
        """
        self._match_termination_service.end_match(reason, winner_id, loser_id)

    def get_turn_context_dto(self, for_new_turn=False):
        return TurnContextDto(
            currentPlayerId=self.get_current_player().player_id,
            isPlayer1Turn=self.match_context.is_player1_turn,
            remainingTimeInS=(
                TURN_DURATION_IN_S if for_new_turn else self._get_remaining_turn_time()
            ),
            durationInS=TURN_DURATION_IN_S,
            notifyTurnChange=for_new_turn,
            updatedBoardArray=self.match_context.game_board.to_dto(),
            playerResourceBundle=PlayerResourceBundleDto(
                self.match_context.player1.resources.to_dto(),
                self.match_context.player2.resources.to_dto(),
            ),
        )

    def set_player_as_idle(self, player_id: str):
        """
        Sets the server side player mode to idle.
        """
        if self.get_current_player().player_id != player_id:
            return

        self._match_actions_service.set_player_as_idle()

    def handle_cell_selection(self, cell_row: int, cell_col: int):
        """
        Triggers all of the processing relative to a cell selection.
        """
        self._match_actions_service.handle_cell_selection(cell_row, cell_col)

    def handle_spawn_button(self):
        """
        Triggers all of the processing relative to a spawn request.
        """
        self._match_actions_service.handle_spawn_toggle()

    def handle_spell_button(self, spell_id: int):
        """
        Triggers all of the processing relative to a spell request.
        """
        self._match_actions_service.handle_spell_request(spell_id)

    def force_turn_swap(self):
        """
        Forcefully triggers a turn swap.
        """
        self._turn_watcher_service.force_turn_swap()

    def stop_watching_player_exit(self, player_id: str):
        """
        Stops watching a player exit.
        """
        self._player_exit_watcher_service.stop_watching_player_exit(player_id)

    def watch_player_exit(self, player_id: str):
        """
        Starts watching a player exit, ending the match after a given delay if the player
        does not reconnect.
        """
        self._player_exit_watcher_service.watch_player_exit(player_id)

    def get_current_player(self):
        """Gets the id of the player of whom it is the turn."""
        return (
            self.match_context.player1
            if self.match_context.is_player1_turn
            else self.match_context.player2
        )

    def get_player(self, player_id: str):
        """
        Gets the `PlayerInfoDto` instance associated with the given player id.
        """
        player1 = self.match_context.player1
        player2 = self.match_context.player2
        player_ids = [player1.player_id, player2.player_id]
        self.logger.debug(f"Player ids: {player_ids}")

        if player_id not in player_ids:
            raise ValueError(
                f"The given player id ({player_id}) is not part of this match"
            )

        return player1 if player_id == player_ids[0] else player2

    def get_actions_per_turn(self):
        """
        Returns the actions per turn dictionary.
        """
        return self._match_actions_service.actions_per_turn

    def get_players_resources(self):
        """
        Gets the player resources of both players.

        The first and second elements in the tuple belong to the player1 and player2 respectively.
        """
        player_1 = self.match_context.player1
        player_2 = self.match_context.player2
        return (
            player_1.resources,
            player_2.resources,
        )

    def _get_remaining_turn_time(self):
        """
        Return the current turn's remaining time.
        """
        return self._turn_watcher_service.get_remaining_turn_time()

    def _get_initial_match_context(self, room: Room):
        return MatchContext.get_initial(generate_id(MatchContext), room)


class MatchStatus(Enum):
    WAITING_TO_START = 0
    ONGOING = 1
    ENDED = 2
    ABORTED = 3
