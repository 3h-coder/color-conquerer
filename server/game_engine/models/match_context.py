from dataclasses import dataclass

from game_engine.models.cell import Cell
from game_engine.models.player import Player


@dataclass
class MatchContext:
    id: str
    room_id: str
    board_array: list[list[Cell]]
    current_turn: int
    is_player1_turn: bool
    player1: Player
    player2: Player

    def both_players_are_dead(self):
        return self.player1_is_dead() and self.player2_is_dead()

    def player1_is_dead(self):
        return self._player_is_dead(self.player1)

    def player2_is_dead(self):
        return self._player_is_dead(self.player2)

    def _player_is_dead(self, player: Player):
        return player.resources.current_hp <= 0
