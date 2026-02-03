from typing import TYPE_CHECKING

from config.logging import get_configured_logger

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

    def take_turn(self):
        """
        Called when it's the AI's turn.
        For now, just ends the turn immediately.
        """
        self.logger.info(f"AI player {self.player_id} taking turn")

        # Add a small delay to make it feel more natural
        self._server.socketio.sleep(0.5)

        # End turn
        self.match.force_turn_swap()
