from enum import Enum

from config.logger import logger
from constants.match_constants import DELAY_IN_S_BEFORE_MATCH_EXCLUSION
from dto.cell_info_dto import CellInfoDto, CellState
from dto.match_info_dto import MatchInfoDto
from dto.player_info_dto import PlayerInfoDto
from dto.room_dto import RoomDto
from utils.id_generation_utils import generate_id
from utils.models.sptimer import SPTimer


class MatchHandlerUnit:
    """
    Handles a single ongoing match.
    """

    def __init__(self, room_dto: RoomDto):
        self.match_info = self._get_initial_match_info(room_dto)
        self.status = MatchStatus.WAITING_TO_START
        # TODO: Add a timer to wait a maximum of x seconds for both players to be ready
        self.players_ready = {
            room_dto.player1.playerId: False,
            room_dto.player2.playerId: False,
        }
        self.exit_watcher = SPTimer(
            tick_interval=DELAY_IN_S_BEFORE_MATCH_EXCLUSION,
            on_tick=self._confirm_player_exit,
            max_ticks=1,
        )

    def start_match(self):
        self.status = MatchStatus.ONGOING
        # TODO: current turn info, timer etc.

    def is_waiting_to_start(self):
        return self.status == MatchStatus.WAITING_TO_START

    def is_ongoing(self):
        return self.status == MatchStatus.ONGOING

    def is_ended(self):
        return self.status == MatchStatus.ENDED

    def start_exit_watcher(self, player_info_dto: PlayerInfoDto):
        logger.debug(f"Started exit watcher for the player : {player_info_dto}")
        self.exit_watcher.start()

    def stop_exit_watch(self, player_info_dto: PlayerInfoDto):
        logger.debug(f"Stopping the exit watcher for the player : {player_info_dto}")
        self.exit_watcher.stop()

    def _confirm_player_exit(self, player_info_dto: PlayerInfoDto | None):
        if not player_info_dto:
            logger.warning(
                "Cannot confirm a player exit when the player info is not set"
            )
            return False

        logger.debug(
            f"{DELAY_IN_S_BEFORE_MATCH_EXCLUSION} seconds passed, confirming player exit"
        )
        # TODO: set the winner as the other player
        return True

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
