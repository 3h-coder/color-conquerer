from typing import TYPE_CHECKING
from ai.config.ai_config import MASTER_CRITICAL_HEALTH_THRESHOLD

if TYPE_CHECKING:
    from handlers.match_handler_unit import MatchHandlerUnit


class BaseEvaluator:
    """
    Base class for all AI evaluators.
    Stores match context and player side to avoid passing them repeatedly.
    """

    def __init__(self, match: "MatchHandlerUnit", ai_is_player1: bool):
        self._match = match
        self._match_context = match.match_context
        self._ai_is_player1 = ai_is_player1

    def _is_ai_master_critical_health(self) -> bool:
        """
        Helper method to check if the AI player's master is at critical health.
        Returns True if master HP <= MASTER_CRITICAL_HEALTH_THRESHOLD.
        """
        ai_player = (
            self._match_context.player1
            if self._ai_is_player1
            else self._match_context.player2
        )
        return ai_player.resources.current_hp <= MASTER_CRITICAL_HEALTH_THRESHOLD
