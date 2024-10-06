from enum import Enum
from threading import Event

from flask import copy_current_request_context
from flask_socketio import SocketIO

from config.logger import logger
from constants.match_constants import (
    DELAY_IN_S_BEFORE_MATCH_EXCLUSION,
    DELAY_IN_S_BEFORE_MATCH_HANDLER_UNIT_DELETION,
    DELAY_IN_S_TO_WAIT_FOR_EVERYONE,
    TURN_DURATION_IN_S,
)
from dto.cell_info_dto import CellInfoDto, CellState
from dto.match_closure_dto import EndingReason, MatchClosureDto
from dto.match_info_dto import MatchInfoDto
from dto.player_info_dto import PlayerInfoDto
from dto.room_dto import RoomDto
from utils import session_utils
from utils.id_generation_utils import generate_id


class MatchHandlerUnit:
    """
    Handles a single ongoing match.
    """

    def __init__(self, room_dto: RoomDto):
        self.match_info = self._get_initial_match_info(room_dto)
        self.session_ids = room_dto.sessionIds
        self.match_closure_info = None
        self.status = MatchStatus.WAITING_TO_START
        self.turn_watcher_thread = None
        self.current_player = room_dto.player1  # Player 1 is always the starting one
        # TODO: Add a timer to wait a maximum of x seconds for both players to be ready
        self.players_ready = {
            room_dto.player1.playerId: False,
            room_dto.player2.playerId: False,
        }
        # Events used to cancel an exit watcher task for a specific player, i.e. not kick the player out when they reconnect
        self.player_exit_watch_stop_events = {
            room_dto.player1.playerId: Event(),
            room_dto.player2.playerId: Event(),
        }

    def watch_player_entry(self):
        """
        Waits a specific delay before ending the match if one player could not manage to be ready.
        """
        from server_gate import server

        def end_match_after_delay():
            server.socketio.sleep(DELAY_IN_S_TO_WAIT_FOR_EVERYONE)

            if all(value is False for value in self.players_ready.values()):
                self.end_match(EndingReason.DRAW, server_ref=server)
                return

            for player_id in self.players_ready:
                if not self.players_ready[player_id]:
                    self.end_match(EndingReason.NEVER_JOINED, loser_id=player_id)

        server.socketio.start_background_task(target=end_match_after_delay)

    def start_match(self, turn_swap_event_name):
        """
        Starts the match, setting up the turn watcher.
        """
        self.status = MatchStatus.ONGOING
        self.match_info.currentTurn = 1
        self._trigger_turn_watcher(turn_swap_event_name)

    def is_waiting_to_start(self):
        return self.status == MatchStatus.WAITING_TO_START

    def is_ongoing(self):
        return self.status == MatchStatus.ONGOING

    def is_ended(self):
        return self.status == MatchStatus.ENDED

    def end_match(
        self,
        reason: EndingReason,
        server_ref=None,
        winner_id: str | None = None,
        loser_id: str | None = None,
    ):
        """
        Declares the match as ended, registering the information in a
        dedicated database and removing the room from the room handler.

        Additionally, notifies all players and schedules this match handler unit's garbage collection.
        """
        if self.is_ended():
            logger.debug("Match already ended.")
            return

        if (
            winner_id is None
            and loser_id is None
            and reason not in [EndingReason.DRAW, EndingReason.CONTEXT_FETCHING_FAILURE]
        ):
            raise ValueError("No winner id nor loser id provided")

        if server_ref is None:
            from server_gate import server

            server_ref = server

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
        self.status = MatchStatus.ENDED
        self.match_closure_info = MatchClosureDto(reason.value, winner, loser)

        # TODO: save the match result into a database
        logger.debug(f"Match ended -> {self.match_closure_info}")

        # Notify the users and close the room
        from events.events import Events

        server_ref.socketio.emit(
            Events.SERVER_MATCH_END.value,
            self.match_closure_info.to_dict(),
            to=self.match_info.roomId,
        )
        server_ref.socketio.close_room(self.match_info.roomId)

        from handlers import room_handler

        room_handler.remove_closed_room(self.match_info.roomId)
        # Schedule the deletion of this object
        self._schedule_garbage_collection(server_ref)

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

        from server_gate import server

        @copy_current_request_context
        def exit_timer():
            logger.debug(f"Starting the exit watch for the player {player_id}")
            self._polling_sleep(
                server.socketio, DELAY_IN_S_BEFORE_MATCH_EXCLUSION, stop_event
            )

            if stop_event.is_set():
                logger.debug("The exit watch was stopped")
                return

            self.end_match(
                EndingReason.PLAYER_LEFT, server_ref=server, loser_id=player_id
            )
            session_utils.clear_match_info()

        server.socketio.start_background_task(target=exit_timer)

    def _schedule_garbage_collection(self, server_ref):
        """
        Schedules the deletion of this match handler unit.
        """
        if server_ref is None:
            from server_gate import server

            server_ref = server

        def delete_self():
            server_ref.socketio.sleep(DELAY_IN_S_BEFORE_MATCH_HANDLER_UNIT_DELETION)

            room_id = self.match_info.roomId
            logger.debug(f"Deleting the match handler unit for the room {room_id}")

            from handlers import match_handler

            del match_handler.units[self.match_info.roomId]

        server_ref.socketio.start_background_task(target=delete_self)

    def _trigger_turn_watcher(self, turn_swap_event_name):
        from server_gate import server

        def watch_turns():
            while not self.is_ended():
                server.socketio.sleep(TURN_DURATION_IN_S)
                if self.is_ended():
                    return

                self.match_info.currentTurn += 1
                self.current_player = (
                    self.match_info.player1
                    if self.current_player == self.match_info.player2
                    else self.match_info.player2
                )
                server.socketio.emit(turn_swap_event_name, to=self.match_info.roomId)

        self.turn_watcher_thread = server.socketio.start_background_task(
            target=watch_turns
        )

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
            currentTurn=0,
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
