from typing import TYPE_CHECKING

from game_engine.models.dtos.match_context import MatchContext

if TYPE_CHECKING:
    from game_engine.models.actions.action import Action


class ActionHook:
    """
    As opposed to callbacks, an action hook must be systematically
    called before the action is performed.
    """

    def trigger(self, action: "Action", match_context: MatchContext):
        raise NotImplementedError
