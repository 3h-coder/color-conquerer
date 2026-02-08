from typing import TYPE_CHECKING, List, Optional, TypeVar, Callable

if TYPE_CHECKING:
    from handlers.match_handler_unit import MatchHandlerUnit
    from game_engine.models.actions.base_action import BaseAction

T = TypeVar("T", bound="BaseAction")


class BaseDecider:
    """
    Base class for all AI decision makers.
    Stores match context and player side to avoid passing them repeatedly.
    """

    def __init__(self, match: "MatchHandlerUnit", ai_is_player1: bool):
        self._match = match
        self._match_context = match.match_context
        self._ai_is_player1 = ai_is_player1

    @property
    def game_board(self):
        """Returns the current game board."""
        return self._match_context.game_board

    def _get_transient_board(self):
        """
        Returns a cloned version of the board suitable for "what-if" calculations.
        Prevents marking real board cells with transient states like CAN_BE_SPAWNED_INTO.
        """
        return self.game_board.clone_as_transient()

    def _pick_best_action(
        self,
        actions: List[T],
        score_fn: Callable[[T], float],
    ) -> Optional[T]:
        """
        Generic helper to pick the action with the highest score.
        Returns None if no actions are provided or all scores are too low.
        """
        if not actions:
            return None

        best_action = None
        max_score = -1.0

        for action in actions:
            score = score_fn(action)
            if score > max_score:
                max_score = score
                best_action = action

        return best_action
