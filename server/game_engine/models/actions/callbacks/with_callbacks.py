from game_engine.models.actions.callbacks.action_callback_id import ActionCallBackId
from typing import TYPE_CHECKING, Any, Generator

from game_engine.models.match_context import MatchContext

if TYPE_CHECKING:
    from game_engine.models.actions.callbacks.action_callback import ActionCallback


class WithCallbacks:
    """
    Interface like class for both action and action callbacks to
    implement common callback logic.
    """

    CALLBACKS: set[ActionCallBackId] = set()

    def __init__(self):
        self._callbacks_to_trigger: set["ActionCallback"] = set()

    def has_callbacks_to_trigger(self):
        return self._callbacks_to_trigger is not None and bool(
            self._callbacks_to_trigger
        )

    def get_callbacks_to_trigger(self) -> Generator["ActionCallback", Any, None]:
        """
        Returns the callbacks to trigger in the order they should be triggered,
        while emptying the internal list.
        """
        while self._callbacks_to_trigger:
            yield self._callbacks_to_trigger.pop()

    def register_callbacks(self, match_context: MatchContext):
        raise NotImplementedError
