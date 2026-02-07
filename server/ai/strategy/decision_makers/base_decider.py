from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from handlers.match_handler_unit import MatchHandlerUnit


class BaseDecider:
    """
    Base class for all AI decision makers.
    Stores match context and player side to avoid passing them repeatedly.
    """

    def __init__(self, match: "MatchHandlerUnit", ai_is_player1: bool):
        self._match = match
        self._match_context = match.match_context
        self._ai_is_player1 = ai_is_player1

    def _get_transient_board(self):
        """
        Returns a cloned version of the board suitable for "what-if" calculations.
        Prevents marking real board cells with transient states like CAN_BE_SPAWNED_INTO.
        """
        return self._match_context.game_board.clone_as_transient()
