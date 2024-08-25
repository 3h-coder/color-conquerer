from enum import Enum

from config.logger import logger
from dto.cell_info_dto import CellInfoDto, CellState
from dto.match_info_dto import MatchInfoDto
from dto.player_info_dto import PlayerInfoDto
from dto.room_dto import RoomDto
from utils.id_generation_utils import generate_id


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

    def start_match(self):
        self.status = MatchStatus.ONGOING
        # TODO: current turn info, timer etc.

    def is_waiting_to_start(self):
        return self.status == MatchStatus.WAITING_TO_START

    def is_ongoing(self):
        return self.status == MatchStatus.ONGOING

    def is_ended(self):
        return self.status == MatchStatus.ENDED

    def end_match(self, reason: str):
        # TODO: set the winner as the other player
        self.status = MatchStatus.ENDED
        logger.debug(f"Ended the match because : {reason}")

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
