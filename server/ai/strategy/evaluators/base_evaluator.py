from typing import TYPE_CHECKING

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
