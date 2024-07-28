import asyncio
from enum import Enum

from config.logger import logger
from dto.cell_info_dto import CellInfoDto, CellState
from dto.match_info_dto import MatchInfoDto
from dto.player_info_dto import PlayerInfoDto
from dto.room_dto import RoomDto
from helpers.id_generation_helper import generate_id


class MatchHandlerUnit:
    """
    Handles a single ongoing match.
    """

    def __init__(self, room_dto: RoomDto):
        self.match_info = self._get_starting_match_info(room_dto)
        self.status = MatchStatus.WAITING_TO_START
        self.exit_watcher = None

    def start_exit_watcher(self, player_info_dto: PlayerInfoDto):
        logger.debug("Started exit watcher")
        self.exit_watcher = asyncio.create_task(
            self._confirm_player_exit(player_info_dto)
        )

    async def _confirm_player_exit(self, player_info_dto: PlayerInfoDto):
        if player_info_dto is None:
            return None

        delay_seconds = 30
        # Wait 30 seconds for it to get eventually cancelled
        await asyncio.sleep(delay_seconds)
        logger.debug(f"{delay_seconds} seconds passed confirming player exit")
        # TODO: set the winner as the other player instead of returning that
        return player_info_dto

    def _get_starting_match_info(self, room_dto: RoomDto):
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
