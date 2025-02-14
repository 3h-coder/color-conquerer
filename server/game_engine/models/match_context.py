from dataclasses import dataclass

from dto.match_context_dto import MatchContextDto
from game_engine.models.game_board import GameBoard
from game_engine.models.player import Player
from game_engine.models.room import Room


@dataclass
class MatchContext:
    """
    Stores both players' information on top of additional information
    such as the room's id or current board.
    """

    id: str
    room_id: str
    game_board: GameBoard
    current_turn: int
    is_player1_turn: bool
    player1: Player
    player2: Player

    def to_dto(self):
        return MatchContextDto(
            id=self.id,
            roomId=self.room_id,
            boardArray=self.game_board.to_dto(),
            currentTurn=self.current_turn,
            player1=self.player1.to_dto(),
            player2=self.player2.to_dto(),
        )

    @staticmethod
    def get_initial(id: str, room: Room):
        return MatchContext(
            id=id,
            room_id=room.id,
            game_board=GameBoard.get_initial(),
            current_turn=0,
            is_player1_turn=False,
            player1=Player.get_initial(
                player_id=room.player1_queue_dto.playerId,
                individual_room_id=room.player1_room_id,
                user_id=room.player1_queue_dto.user.id,
                is_player_1=True,
            ),
            player2=Player.get_initial(
                player_id=room.player2_queue_dto.playerId,
                individual_room_id=room.player2_room_id,
                user_id=room.player2_queue_dto.user.id,
                is_player_1=False,
            ),
        )

    def get_player_resources(self, player1: bool):
        return self.player1.resources if player1 else self.player2.resources

    def both_players_are_dead(self):
        return self.player1_is_dead() and self.player2_is_dead()

    def player1_is_dead(self):
        return self._player_is_dead(self.player1)

    def player2_is_dead(self):
        return self._player_is_dead(self.player2)

    def _player_is_dead(self, player: Player):
        return player.resources.current_hp <= 0
