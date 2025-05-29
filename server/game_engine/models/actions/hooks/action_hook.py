from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game_engine.models.actions.action import Action
    from game_engine.models.match.match_context import MatchContext


class ActionHook:
    """
    As opposed to callbacks, an action hook must be systematically
    called before the action is performed.
    """

    def trigger(self, action: "Action", match_context: "MatchContext"):
        raise NotImplementedError
