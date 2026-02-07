from typing import TYPE_CHECKING

from config.logging import get_configured_logger
from ai.strategy.evaluators.board.board_evaluator import BoardEvaluator

if TYPE_CHECKING:
    from handlers.match_handler_unit import MatchHandlerUnit


class AIPlayer:
    """
    Represents an AI-controlled player that makes automated decisions.
    Currently just passes its turn without taking any actions.
    """

    def __init__(self, match_handler_unit: "MatchHandlerUnit", player_id: str):
        self.match = match_handler_unit
        self.player_id = player_id
        self.logger = get_configured_logger(__name__)
        self._server = match_handler_unit.server

        # Initialize evaluator
        self.board_evaluator = BoardEvaluator()

        # Determine if AI is player 1 or player 2
        self.ai_is_player1 = (
            match_handler_unit.match_context.player1.player_id == player_id
        )

    def take_turn(self):
        """
        Called when it's the AI's turn.
        For now, evaluates the board and logs the results, then ends the turn.
        """
        self.logger.info(f"AI player {self.player_id} taking turn")

        # Evaluate the board state
        evaluation = self.board_evaluator.evaluate(
            self.match.match_context, ai_is_player1=self.ai_is_player1
        )

        # Log evaluation results for debugging
        self.logger.info(f"\n{evaluation}")

        # Add a small delay to make it feel more natural
        self._server.socketio.sleep(5)

        # End turn
        self.match.force_turn_swap()
