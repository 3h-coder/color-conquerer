from enum import Enum

from flask_socketio import emit

from config.logger import logger
from dto.cell_info_dto import CellInfoDto, CellState
from dto.match_closure_dto import MatchClosureDto
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
        self.match_closure_info = None
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

    def end_match(
        self, reason: str, winner_id: str | None = None, loser_id: str | None = None
    ):
        player1 = self.match_info.player1
        player2 = self.match_info.player2
        player_ids = [player1.playerId, player2.playerId]

        # Validate provided IDs
        if winner_id is None and loser_id is None:
            raise ValueError("No winner id nor loser id provided")

        if winner_id is not None and winner_id not in player_ids:
            raise ValueError("The winner id does not correspond to any player id")

        if loser_id is not None and loser_id not in player_ids:
            raise ValueError("The loser id does not correspond to any player id")

        # Determine winner and loser
        if winner_id:
            winner = player1 if winner_id == player1.playerId else player2
            loser = player2 if winner_id == player1.playerId else player1
        else:
            loser = player1 if loser_id == player1.playerId else player2
            winner = player2 if loser_id == player1.playerId else player1

        # Update match status
        self.status = MatchStatus.ENDED
        self.match_closure_info = MatchClosureDto(reason, winner, loser)

        # TODO: save the match result into a database
        logger.debug(f"Match ended -> {self.match_closure_info}")

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
