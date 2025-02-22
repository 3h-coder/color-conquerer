from typing import TYPE_CHECKING

from dto.action_callback_dto import ActionCallbackDto
from game_engine.models.actions.callbacks.action_callback_id import ActionCallBackId
from game_engine.models.match_context import MatchContext

if TYPE_CHECKING:
    from game_engine.models.actions.action import Action


class ActionCallback:
    """
    Defines an action that is indirectly triggered by another.
    """

    ID = ActionCallBackId.NONE

    def __init__(self, parent_action: "Action"):
        self.parent_action = parent_action

    def __eq__(self, other):
        return (
            isinstance(other, ActionCallback)
            and self.ID == other.ID
            and self.parent_action == other.parent_action
        )

    def __hash__(self):
        return hash((self.ID, self.parent_action))

    def to_dto(self):
        return ActionCallbackDto(self.ID, self.parent_action)

    def can_be_triggered(self, match_context: MatchContext):
        raise NotImplementedError

    def trigger(self, match_context: MatchContext):
        raise NotImplementedError
