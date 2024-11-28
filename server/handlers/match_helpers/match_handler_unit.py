from enum import Enum
from threading import Event

from flask import copy_current_request_context, request
from flask_socketio import SocketIO

from config.logging import get_configured_logger
from constants.match_constants import (
    BOARD_SIZE,
    DELAY_IN_S_BEFORE_MATCH_EXCLUSION,
    DELAY_IN_S_BEFORE_MATCH_HANDLER_UNIT_DELETION,
    DELAY_IN_S_TO_WAIT_FOR_EVERYONE,
    TURN_DURATION_IN_S,
)
from dto.cell_info_dto import CellInfoDto, CellState
from dto.partial_match_closure_dto import PartialMatchClosureDto
from dto.partial_player_game_info_dto import PartialPlayerGameInfoDto
from dto.player_info_bundle_dto import PlayerGameInfoBundleDto
from dto.server_only.match_closure_dto import EndingReason, MatchClosureDto
from dto.server_only.match_info_dto import MatchInfoDto
from dto.server_only.room_dto import RoomDto
from dto.turn_info_dto import TurnInfoDto
from handlers.match_helpers.client_notifications import (
    notify_match_end,
    notify_match_start,
)
from handlers.match_helpers.player_entry_watcher_service import (
    PlayerEntryWatcherService,
)
from handlers.match_helpers.player_exit_watcher_service import PlayerExitWatcherService
from handlers.match_helpers.turn_watcher_service import TurnWatcherService
from server_gate import get_server
from utils import session_utils
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

        self._status = MatchStatus.WAITING_TO_START

        self._player_entry_watcher_service = PlayerEntryWatcherService(self)

        self._player_exit_watcher_service = PlayerExitWatcherService(self)

        self._turn_watcher_service = TurnWatcherService(self)

        # Dto which we use to share/save the final match data before disposing the handler unit
        self.match_closure_info = None

    def is_waiting_to_start(self):
        return self._status == MatchStatus.WAITING_TO_START

    def is_ongoing(self):
        return self._status == MatchStatus.ONGOING

    def is_ended(self):
        return self._status == MatchStatus.ENDED

    def is_cancelled(self):
        return self._status == MatchStatus.ABORTED

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
                f"Can only start a match that is waiting to start. The match status is {self._status.name}"
            )
            return

        self.logger.info(f"Starting the match in the room {self.match_info.roomId}")

        self._status = MatchStatus.ONGOING
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
        self.logger.info(
            f"Match cancellation requested for the match in the room {self.match_info.roomId}"
        )

        if not self.is_waiting_to_start():
            self.logger.warning(
                f"Can only cancel a match that is waiting to start. The match status is {self._status.name}"
            )
            return

        # TODO: call a match cleanup service/helper/handler
        self._status = MatchStatus.ABORTED
        self._schedule_garbage_collection()

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
        # TODO: call a match cleanup service/helper/handler
        self.logger.info(
            f"Received termination request for the match in the room {self.match_info.roomId}"
        )

        if not self.is_ongoing():
            self.logger.warning(
                f"Can only end a match that is ongoing. The match status is {self._status.name}"
            )
            return

        if winner_id is None and loser_id is None and reason != EndingReason.DRAW:
            raise ValueError("No winner id nor loser id provided")

        player1 = self.match_info.player1
        player2 = self.match_info.player2
        winner = None
        loser = None

        if winner_id is not None:
            winner = self.get_player(winner_id)
            loser = player1 if winner == player2 else player2
        else:
            loser = self.get_player(loser_id)
            winner = player1 if loser == player2 else player2

        # Update match status
        self._status = MatchStatus.ENDED
        self.match_closure_info = MatchClosureDto(reason.value, winner, loser)

        # TODO: save the match result into a database
        self.logger.debug(f"Match ended -> {self.match_closure_info}")

        # Notify the users and close the room
        notify_match_end(
            PartialMatchClosureDto.from_match_closure_dto(self.match_closure_info),
            self.match_info.roomId,
        )
        self.server.socketio.close_room(self.match_info.roomId)

        from handlers import room_handler

        room_handler.remove_closed_room(self.match_info.roomId)
        # Schedule the deletion of this object
        self._schedule_garbage_collection()

    def get_turn_info(self, for_new_turn=False):
        players_game_info = [
            PartialPlayerGameInfoDto.from_player_game_info(player_game_info)
            for player_game_info in self._get_players_game_info()
        ]
        player1_game_info = players_game_info[0]
        player2_game_info = players_game_info[1]

        return TurnInfoDto(
            currentPlayerId=self.get_current_player().playerId,
            isPlayer1Turn=self.match_info.isPlayer1Turn,
            durationInS=(
                TURN_DURATION_IN_S if for_new_turn else self._get_remaining_turn_time()
            ),
            playerInfoBundle=PlayerGameInfoBundleDto(
                player1_game_info, player2_game_info
            ),
            notifyTurnChange=for_new_turn,
        )

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

        if player_id not in player_ids:
            raise ValueError("Could not get the player from the player id")

        return player1 if player_id == player_ids[0] else player2

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

    def _schedule_garbage_collection(self):
        """
        Schedules the deletion of this match handler unit and the associated room.
        """

        def delete_self_and_room():
            self.server.socketio.sleep(DELAY_IN_S_BEFORE_MATCH_HANDLER_UNIT_DELETION)

            room_id = self.match_info.roomId
            self.logger.debug(f"Deleting the match handler unit for the room {room_id}")

            from handlers import match_handler, room_handler

            if room_id in room_handler.closed_rooms:
                room_handler.remove_closed_room(room_id)

            if room_id not in match_handler.units:
                self.logger.warning(
                    f"Tried to delete a match handler unit that did not exist : {room_id}"
                )
                return

            del match_handler.units[room_id]

        self.server.socketio.start_background_task(target=delete_self_and_room)

    def _get_initial_match_info(self, room_dto: RoomDto):
        return MatchInfoDto.get_initial_match_info(
            generate_id(MatchInfoDto), room_dto, self._get_starting_board_array()
        )

    def _get_starting_board_array(self):
        # ⚠️ the board size must never change
        # TODO: create unit tests to ensure that

        board = [
            [
                CellInfoDto(owner=0, rowIndex=i, columnIndex=j, state=CellState.IDLE)
                for j in range(BOARD_SIZE)
            ]
            for i in range(BOARD_SIZE)
        ]

        # initialize the cell[2][7] as owned by player1 and the cell[12][7] by player2
        board[1][5].owner = 1
        board[1][5].state = CellState.CAPTURED
        board[9][5].owner = 2
        board[9][5].state = CellState.CAPTURED

        return board


class MatchStatus(Enum):
    WAITING_TO_START = 0
    ONGOING = 1
    ENDED = 2
    ABORTED = 3
