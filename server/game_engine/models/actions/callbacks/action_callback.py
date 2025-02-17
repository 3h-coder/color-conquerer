from dto.action_callback_dto import ActionCallbackDto
from game_engine.models.actions.action import Action
from game_engine.models.actions.callbacks.action_callback_id import ActionCallBackId
from game_engine.models.match_context import MatchContext


class ActionCallback:
    """
    Defines an action that is indirectly triggered by another.
    """

    ID = ActionCallBackId.NONE

    def __init__(self, parent_action: Action):
        self.parent_action = parent_action

    def to_dto(self):
        return ActionCallbackDto(self.ID)

    def can_be_triggered(self, match_context: MatchContext):
        raise NotImplementedError

    def trigger(self, match_context: MatchContext):
        raise NotImplementedError
