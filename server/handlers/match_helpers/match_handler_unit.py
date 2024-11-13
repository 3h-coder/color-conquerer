from datetime import datetime
from enum import Enum
from threading import Event

from flask import copy_current_request_context, request
from flask_socketio import SocketIO

from config.logging import get_configured_logger
from constants.match_constants import (
    DELAY_IN_S_BEFORE_MATCH_EXCLUSION,
    DELAY_IN_S_BEFORE_MATCH_HANDLER_UNIT_DELETION,
    DELAY_IN_S_TO_WAIT_FOR_EVERYONE,
    TURN_DURATION_IN_S,
)
from dto.cell_info_dto import CellInfoDto, CellState
from dto.partial_match_closure_dto import PartialMatchClosureDto
from dto.server_only.match_closure_dto import EndingReason, MatchClosureDto
from dto.server_only.match_info_dto import MatchInfoDto
from dto.server_only.player_info_dto import PlayerInfoDto
from dto.server_only.room_dto import RoomDto
from dto.turn_info_dto import TurnInfoDto
from server_gate import get_server
from utils import session_utils
from utils.id_generation_utils import generate_id


class MatchHandlerUnit:
    """
    Handles a single ongoing match.
    """

    def __init__(self, room_dto: RoomDto):
        self.logger = get_configured_logger(__name__)
        self._server = get_server()

        self.match_info = self._get_initial_match_info(room_dto)

        # Dictionary with the key being the session id and the value the player id
        # May be used when needed to find a player from its session
        self._session_ids = room_dto.sessionIds

        self._status = MatchStatus.WAITING_TO_START

        # Thread responsible for swapping the turns between players
        self._turn_watcher_thread = None
        self._turn_start_time: datetime = None

        self.players_ready = {
            room_dto.player1.playerId: False,
            room_dto.player2.playerId: False,
        }
        # Events used to cancel an exit watcher task for a specific player, i.e. not kick the player out when they reconnect
        self.player_exit_watch_stop_events = {
            room_dto.player1.playerId: Event(),
            room_dto.player2.playerId: Event(),
        }

        # Dto which we use to share/save the final match data before disposing the handler unit
        self.match_closure_info = None

    def is_waiting_to_start(self):
        return self._status == MatchStatus.WAITING_TO_START

    def is_ongoing(self):
        return self._status == MatchStatus.ONGOING

    def is_ended(self):
        return self._status == MatchStatus.ENDED

    def watch_player_entry(self):
        """
        Waits a specific delay before ending the match if one player could not manage to be ready.
        """

        def end_match_after_delay():
            self._server.socketio.sleep(DELAY_IN_S_TO_WAIT_FOR_EVERYONE)

            if all(value is False for value in self.players_ready.values()):
                self.end(EndingReason.DRAW)
                return

            for player_id in self.players_ready:
                if not self.players_ready[player_id]:
                    self.end(EndingReason.NEVER_JOINED, loser_id=player_id)

        self._server.socketio.start_background_task(target=end_match_after_delay)

    def start(self):
        """
        Starts the match, setting up the turn watcher and notifying the clients.
        """
        from events.events import Events

        self.logger.info(f"Starting the match in the room {self.match_info.roomId}")

        self._status = MatchStatus.ONGOING
        self.match_info.currentTurn = 1
        self.match_info.isPlayer1Turn = True

        self._trigger_turn_watcher()

        # notify the clients
        self._server.socketio.emit(
            Events.SERVER_MATCH_START.value,
            TurnInfoDto(
                self.match_info.player1.playerId,
                self.match_info.isPlayer1Turn,
                TURN_DURATION_IN_S,
            ).to_dict(),
            to=self.match_info.roomId,
        )

    def cancel(self):
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
        self.logger.info(f"Terminating the match in the room {self.match_info.roomId}")

        if self.is_ended():
            self.logger.debug("Match already ended.")
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
        from events.events import Events

        self._server.socketio.emit(
            Events.SERVER_MATCH_END.value,
            PartialMatchClosureDto.from_match_closure_dto(
                self.match_closure_info
            ).to_dict(),
            to=self.match_info.roomId,
        )
        self._server.socketio.close_room(self.match_info.roomId)

        from handlers import room_handler

        room_handler.remove_closed_room(self.match_info.roomId)
        # Schedule the deletion of this object
        self._schedule_garbage_collection()

    def get_remaining_turn_time(self):
        """Returns the remining time in seconds for the current turn"""
        elapsed_time = datetime.now() - self._turn_start_time
        return max(0, TURN_DURATION_IN_S - elapsed_time.seconds)

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

            self.end(EndingReason.PLAYER_LEFT, loser_id=player_id)
            session_utils.clear_match_info()

        self._server.socketio.start_background_task(target=exit_timer)

    def get_current_player_id(self):
        """Gets the id of the player of whom it is the turn"""
        return (
            self.match_info.player1.playerId
            if self.match_info.isPlayer1Turn
            else self.match_info.player2.playerId
        )

    def _trigger_turn_watcher(self):
        """
        Triggers the background task that will handle turn swaping.
        """

        from events.events import Events

        def watch_turns():
            while not self.is_ended():
                self._turn_start_time = datetime.now()
                self._server.socketio.sleep(TURN_DURATION_IN_S)
                if self.is_ended():
                    return

                # Increment the turn count
                self.match_info.currentTurn += 1
                # Swap the current player's turn
                self.match_info.isPlayer1Turn = not self.match_info.isPlayer1Turn

                # Notify the turn change to players
                self._server.socketio.emit(
                    Events.SERVER_TURN_SWAP.value,
                    TurnInfoDto(
                        self.get_current_player_id(),
                        self.match_info.isPlayer1Turn,
                        TURN_DURATION_IN_S,
                    ).to_dict(),
                    to=self.match_info.roomId,
                )

        self._turn_watcher_thread = self._server.socketio.start_background_task(
            target=watch_turns
        )

    def _schedule_garbage_collection(self):
        """
        Schedules the deletion of this match handler unit and the associated room.
        """

        def delete_self_and_room():
            self._server.socketio.sleep(DELAY_IN_S_BEFORE_MATCH_HANDLER_UNIT_DELETION)

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

        self._server.socketio.start_background_task(target=delete_self_and_room)

    def _polling_sleep(
        self, socketio: SocketIO, sleep_duration_in_s, stop_event: Event
    ):
        check_interval_in_s = 0.05  # 50 ms
        elapsed = 0

        while elapsed < sleep_duration_in_s:
            if stop_event.is_set():
                return
            socketio.sleep(check_interval_in_s)
            elapsed += check_interval_in_s

    def get_player(self, player_id: str):
        player1 = self.match_info.player1
        player2 = self.match_info.player2
        player_ids = [player1.playerId, player2.playerId]

        if player_id not in player_ids:
            raise ValueError("Could not get the player from the player id")

        if player_id == player_ids[0]:
            return player1

        return player2

    def _get_initial_match_info(self, room_dto: RoomDto):
        return MatchInfoDto(
            id=generate_id(MatchInfoDto),
            roomId=room_dto.id,
            boardArray=self._get_starting_board_array(),
            currentTurn=0,
            isPlayer1Turn=False,
            totalTurnDurationInS=TURN_DURATION_IN_S,
            player1=PlayerInfoDto(
                user=room_dto.player1.user,
                playerId=room_dto.player1.playerId,
                isPlayer1=True,
            ),
            player2=PlayerInfoDto(
                user=room_dto.player2.user,
                playerId=room_dto.player2.playerId,
                isPlayer1=False,
            ),
        )

    def _get_starting_board_array(self):
        # ⚠️ the board size must never change
        # TODO: create unit tests to ensure that
        board_size = 15

        board = [
            [
                CellInfoDto(owner=0, rowIndex=i, columnIndex=j, state=CellState.IDLE)
                for j in range(board_size)
            ]
            for i in range(board_size)
        ]

        # initialize the cell[2][7] as owned by player1 and the cell[12][7] by player2
        board[2][7].owner = 1
        board[2][7].state = CellState.CAPTURED
        board[12][7].owner = 2
        board[12][7].state = CellState.CAPTURED

        return board


class MatchStatus(Enum):
    WAITING_TO_START = 0
    ONGOING = 1
    ENDED = 2
    ABORTED = 3
