from enum import Enum

from config.logging import get_configured_logger
from constants.match_constants import BOARD_SIZE, TURN_DURATION_IN_S
from dto.server_only.match_closure_dto import EndingReason
from dto.server_only.match_info_dto import MatchInfoDto
from dto.server_only.room_dto import RoomDto
from dto.turn_info_dto import TurnInfoDto
from handlers.match_helpers.client_notifications import notify_match_start
from handlers.match_helpers.match_actions_service import MatchActionsService
from handlers.match_helpers.match_termination_service import MatchTerminationService
from handlers.match_helpers.player_entry_watcher_service import (
    PlayerEntryWatcherService,
)
from handlers.match_helpers.player_exit_watcher_service import PlayerExitWatcherService
from handlers.match_helpers.turn_watcher_service import TurnWatcherService
from server_gate import get_server
from utils.board_utils import create_starting_board, to_client_board_dto
from utils.id_generation_utils import generate_id


class MatchHandlerUnit:
    """
    Handles a single ongoing match.
    Manages the whole lifecyle (start to end) partly thanks to underlying helper classes instances.
    """

    def __init__(self, room_dto: RoomDto):
        self.logger = get_configured_logger(__name__)
        self.server = get_server()

        self.match_info: MatchInfoDto = self._get_initial_match_info(room_dto)

        # Dictionary with the key being the session id and the value the player id
        # May be used when needed to find a player from its session
        self._session_ids = room_dto.sessionIds

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
            f"Match start requested for the match in the room {self.match_info.roomId}"
        )

        if not self.is_waiting_to_start():
            self.logger.warning(
                f"Can only start a match that is waiting to start. The match status is {self.status.name}"
            )
            return

        self.logger.info(f"Starting the match in the room {self.match_info.roomId}")

        self.status = MatchStatus.ONGOING
        self.match_info.currentTurn = 1
        self.match_info.isPlayer1Turn = True

        # Trigger the turn watcher service to process player turns
        self._turn_watcher_service.trigger()

        # notify the clients
        notify_match_start(
            self.get_turn_info(for_new_turn=True),
            self.match_info.roomId,
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

    def get_turn_info(self, for_new_turn=False):
        return TurnInfoDto(
            currentPlayerId=self.get_current_player().playerId,
            isPlayer1Turn=self.match_info.isPlayer1Turn,
            durationInS=(
                TURN_DURATION_IN_S if for_new_turn else self._get_remaining_turn_time()
            ),
            totalTurnDurationInS=TURN_DURATION_IN_S,
            notifyTurnChange=for_new_turn,
            playerGameInfoBundle=self.match_info.get_player_info_bundle(),
            updatedBoardArray=to_client_board_dto(self.match_info.boardArray),
        )

    def set_player_as_idle(self, player_id: str):
        """
        Sets the server side player mode to idle.
        """
        if self.get_current_player().playerId != player_id:
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
            self.match_info.player1
            if self.match_info.isPlayer1Turn
            else self.match_info.player2
        )

    def get_player(self, player_id: str):
        """
        Gets the `PlayerInfoDto` instance associated with the given player id.
        """
        player1 = self.match_info.player1
        player2 = self.match_info.player2
        player_ids = [player1.playerId, player2.playerId]
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

    def _get_players_game_info(self):
        """
        Gets the player game info of both players.
        """
        player_1 = self.match_info.player1
        player_2 = self.match_info.player2
        return (
            player_1.playerGameInfo,
            player_2.playerGameInfo,
        )

    def _get_remaining_turn_time(self):
        """
        Return the current turn's remaining time.
        """
        return self._turn_watcher_service.get_remaining_turn_time()

    def _get_initial_match_info(self, room_dto: RoomDto):
        return MatchInfoDto.get_initial_match_info(
            generate_id(MatchInfoDto), room_dto, self._get_starting_board_array()
        )

    def _get_starting_board_array(self):
        # ⚠️ the board size must never change
        # TODO: create unit tests to ensure that

        board = create_starting_board(BOARD_SIZE)

        # Initialize the master cells
        player1_master_cell = board[1][5]
        player2_master_cell = board[9][5]

        player1_master_cell.set_owned_by_player1()
        player1_master_cell.isMaster = True

        player2_master_cell.set_owned_by_player2()
        player2_master_cell.isMaster = True

        # Initialize mana bubbles
        board[6][5].set_as_mana_bubble()
        board[5][1].set_as_mana_bubble()
        board[5][9].set_as_mana_bubble()

        return board


class MatchStatus(Enum):
    WAITING_TO_START = 0
    ONGOING = 1
    ENDED = 2
    ABORTED = 3
