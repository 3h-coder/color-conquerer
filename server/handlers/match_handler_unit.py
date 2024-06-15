import uuid

from dto.cell_info_dto import CellInfoDto, CellState
from dto.match_info_dto import MatchInfoDto
from dto.player_info_dto import PlayerInfoDto
from dto.room_dto import RoomDto
from helpers.board_helper import display_board_owners
from helpers.id_generation_helper import generate_id


class MatchHandlerUnit:
    """
    Handles a single match on a separate thread.
    """

    def __init__(self, room_dto: RoomDto):
        self.match_info = self._get_starting_match_info(room_dto)

    def _get_starting_match_info(self, room_dto: RoomDto):
        return MatchInfoDto(
            id=generate_id(MatchInfoDto),
            roomId=room_dto.id,
            boardArray=self._get_starting_board_array(),
            player1=PlayerInfoDto(
                user=room_dto.player1.user,
                playerId=room_dto.player1.playerId,
                controlledCells=[],
            ),
            player2=PlayerInfoDto(
                user=room_dto.player2.user,
                playerId=room_dto.player2.playerId,
                controlledCells=[],
            ),
            currentTurn=0,
            started=False,
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
        board[12][7].owner = 2

        return board
