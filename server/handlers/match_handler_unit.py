import functools
from threading import Lock

from config.logging import get_configured_logger
from constants.match_constants import TURN_DURATION_IN_S
from dto.game_state.game_context_dto import GameContextDto
from dto.game_state.turn_context_dto import TurnContextDto
from game_engine.models.dtos.room import Room
from game_engine.models.match.cancellation_reason import CancellationReason
from game_engine.models.match.match_closure_info import EndingReason
from game_engine.models.match.match_context import MatchContext
from game_engine.models.turn.turn_state import TurnState
from handlers.match_services.enums.match_status import MatchStatus
from handlers.match_services.match_actions_service import MatchActionsService
from handlers.match_services.match_start_service import MatchStartService
from handlers.match_services.match_termination_service import MatchTerminationService
from handlers.match_services.player_entry_watcher_service import (
    PlayerEntryWatcherService,
)
from handlers.match_services.player_exit_watcher_service import PlayerExitWatcherService
from handlers.match_services.player_inactivity_watcher_service import (
    PlayerInactivityWatcherService,
)
from handlers.match_services.turn_watcher_service import TurnWatcherService
from server_gate import get_server
from utils import logging_utils
from utils.id_generation_utils import generate_id


class MatchHandlerUnit:
    """
    Handles a single ongoing match.
    Manages the whole lifecyle (start to end) partly thanks to underlying helper classes instances.
    """

    def __init__(self, room: Room):
        self.logger = get_configured_logger(
            __name__,
            prefix_getter=lambda: logging_utils.flask_request_remote_addr_prefix(),
        )
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

        # Some successive emit events need to be secured with a lock
        # to ensure they do happen in the same "transaction"
        self.lock = Lock()

        self._match_start_service = MatchStartService(self)

        self._match_termination_service = MatchTerminationService(self)

        self._match_actions_service = MatchActionsService(self)

        self._player_entry_watcher_service = PlayerEntryWatcherService(self)

        self._player_exit_watcher_service = PlayerExitWatcherService(self)

        self._player_inactivity_watcher_service = PlayerInactivityWatcherService(self)

        self._turn_watcher_service = TurnWatcherService(self)
        self._turn_watcher_service.add_external_callbacks(
            self._match_actions_service.reset_for_new_turn,
            self._player_inactivity_watcher_service.on_turn_swap,
        )

    # region Lifecycle

    def start(self, with_countdown: bool):
        """
        Starts the match, setting up the turn watcher and notifying the clients.
        """
        if with_countdown:
            self._match_start_service.countdown_and_start()
        else:
            self._match_start_service.start()

    def cancel(
        self, cancellation_reason: CancellationReason, penalized_player_id: str = ""
    ):
        """
        Cancels the match.
        """
        self._match_termination_service.cancel_match(
            cancellation_reason, penalized_player_id=penalized_player_id
        )

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

    # endregion

    # region Main API

    # region Player entry observation

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

    # endregion

    # region Player exit observation

    def set_player_as_idle(self, player_id: str):
        """
        Sets the server side player mode to idle.
        """
        if self.get_current_player().player_id != player_id:
            return

        self._match_actions_service.set_player_as_idle()

    def watch_player_exit(self, player_id: str):
        """
        Starts watching a player exit, ending the match after a given delay if the player
        does not reconnect.
        """
        self._player_exit_watcher_service.watch_player_exit(player_id)

    def stop_watching_player_exit(self, player_id: str):
        """
        Stops watching a player exit.
        """
        self._player_exit_watcher_service.stop_watching_player_exit(player_id)

    # endregion

    # region Player actions entry points

    def _reports_player_activity(func):
        """
        Decorator function to automatically report player activity
        and reset the inactivity watchers for the current player.
        """

        @functools.wraps(func)
        def wrapper(self: "MatchHandlerUnit", *args, **kwargs):
            self._player_inactivity_watcher_service.report_activity()
            func(self, *args, **kwargs)

        return wrapper

    @_reports_player_activity
    def handle_cell_selection(self, cell_row: int, cell_col: int):
        """
        Triggers all of the processing relative to a cell selection from the current player.
        """
        self._match_actions_service.handle_cell_selection(cell_row, cell_col)

    @_reports_player_activity
    def handle_spawn_button(self):
        """
        Triggers all of the processing relative to a spawn request from the current player.
        """
        self._match_actions_service.handle_spawn_toggle()

    @_reports_player_activity
    def handle_spell_button(self, spell_id: int):
        """
        Triggers all of the processing relative to a spell request from the current player.
        """
        self._match_actions_service.handle_spell_request(spell_id)

    @_reports_player_activity
    def force_turn_swap(self):
        """
        Forcefully triggers a turn swap.
        """
        self._turn_watcher_service.force_turn_swap()

    # endregion

    # endregion

    # region Getters

    def is_waiting_to_start(self):
        return self.status == MatchStatus.WAITING_TO_START

    def is_ongoing(self):
        return self.status == MatchStatus.ONGOING

    def is_ended(self):
        return self.status == MatchStatus.ENDED

    def is_cancelled(self):
        return self.status == MatchStatus.ABORTED

    def get_turn_context_dto(
        self, for_player1: bool, for_new_turn=False, pre_match_start=False
    ):
        return TurnContextDto(
            currentPlayerId=self.get_current_player().player_id,
            isPlayer1Turn=self.match_context.is_player1_turn,
            remainingTimeInS=(
                TURN_DURATION_IN_S
                if (for_new_turn or pre_match_start)
                else self._get_remaining_turn_time()
            ),
            durationInS=TURN_DURATION_IN_S,
            notifyTurnChange=for_new_turn,
            preMatchStart=pre_match_start,
            gameContext=self.get_game_context_dto(for_player1),
        )

    def get_game_context_dto(self, for_player1: bool):
        return GameContextDto.from_match_context(self.match_context, for_player1)

    def get_current_player(self):
        """Gets the id of the player of whom it is the turn."""
        return self.match_context.get_current_player()

    def get_player(self, player_id: str):
        """
        Gets the `PlayerInfoDto` instance associated with the given player id.
        """
        player1 = self.match_context.player1
        player2 = self.match_context.player2
        player_ids = [player1.player_id, player2.player_id]

        if not player_id or player_id not in player_ids:
            self.logger.error(
                f"The given player id ({player_id}) is not part of this match"
            )
            return None

        return player1 if player_id == player_ids[0] else player2

    def get_actions_per_turn(self, serialized: bool = False):
        """
        Returns the actions per turn dictionary. If `serialized` is True,
        returns the serialized version of the actions per turn.
        """
        return (
            self._match_actions_service.actions_per_turn
            if not serialized
            else self._match_actions_service.actions_per_turn_serialized
        )

    def get_players_resources(self):
        """
        Gets the player resources of both players.

        The first and second elements in the tuple belong to the player1 and player2 respectively.
        """
        return self.match_context.get_both_players_resources()

    def get_individual_player_rooms(self):
        """
        Gets the individual room id for both players.

        The first and second room ids in the tuple belong to the player1 and player2 respectively.
        """
        return self.match_context.get_individual_player_rooms()

    def _get_remaining_turn_time(self):
        """
        Return the current turn's remaining time.
        """
        return self._turn_watcher_service.get_remaining_turn_time()

    def _get_initial_match_context(self, room: Room):
        return MatchContext.get_initial(generate_id(MatchContext), room)

    # endregion

    # region Setters

    def mark_as_ongoing(self):
        """
        WARNING : To only be used in the match start service.

        Allows it not to import MatchStatus.
        """
        self.status = MatchStatus.ONGOING

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

    # endregion
