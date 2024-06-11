import uuid

from dto.cell_info_dto import CellInfoDto
from dto.match_info_dto import MatchInfoDto
from dto.player_info_dto import PlayerInfoDto
from dto.room_dto import RoomDto


class MatchHandlerUnit:
    """
    Handles a single match on a separate thread.
    """

    def __init__(self, room_dto: RoomDto):
        self.id = f"mhu-{uuid.uuid4()}"
        self.match_info = MatchInfoDto(
            id=f"match-{uuid.uuid4()}",
            roomId=room_dto.id,
            boardArray=self._initialize_starting_board_array(),
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

    def _initialize_starting_board_array():
        board_size = 15

        return [
            [
                CellInfoDto(owner=0, rowIndex=i, columnIndex=j, state="")
                for j in range(board_size)
            ]
            for i in range(board_size)
        ]
