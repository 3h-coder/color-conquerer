from dataclasses import dataclass

from game_engine.models.cell import Cell
from game_engine.models.turn_state import TurnState


@dataclass
class TurnContext:
    is_player1_turn: bool
    # shortcut to get the player_id
    current_player_id: str
    remaining_time_in_s: int
    duration_in_s: int
    updated_board_array: list[list[Cell]]
    current_state: TurnState
