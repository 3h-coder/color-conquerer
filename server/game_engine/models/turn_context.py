from dataclasses import dataclass

from dto.player_resources_bundle_dto import PlayerResourceBundleDto
from dto.turn_context_dto import TurnContextDto
from game_engine.models.game_board import GameBoard
from game_engine.models.turn_state import TurnState


@dataclass
class TurnContext:
    is_player1_turn: bool
    # shortcut to get the player_id
    current_player_id: str
    remaining_time_in_s: int
    duration_in_s: int
    updated_board: GameBoard
    current_state: TurnState

    def to_dto(self, notify_turn_change=False):
        return TurnContextDto(
            currentPlayerId=self.current_player_id,
            isPlayer1Turn=self.is_player1_turn,
            remainingTimeInS=self.remaining_time_in_s,
            durationInS=self.duration_in_s,
            notifyTurnChange=notify_turn_change,
            updatedBoardArray=self.updated_board.to_dto(),
            playerResourceBundle=PlayerResourceBundleDto(
                player1Resources=self.current_state.player1_resources.to_dto(),
                player2Resources=self.current_state.player2_resources.to_dto(),
            ),
        )
