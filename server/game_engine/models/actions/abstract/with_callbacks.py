from typing import TYPE_CHECKING, Any, Generator

from game_engine.models.actions.callbacks.action_callback_id import ActionCallBackId

if TYPE_CHECKING:
    from game_engine.models.actions.abstract.action_callback import ActionCallback
    from game_engine.models.match.match_context import MatchContext


class WithCallbacks:
    """
    Interface like class for both action and action callbacks to
    implement common callback logic.
    """

    CALLBACKS: set[ActionCallBackId] = set()

    def __init__(self):
        self._callbacks_to_trigger: list["ActionCallback"] = []

    def has_callbacks_to_trigger(self):
        return bool(self._callbacks_to_trigger)

    def get_callbacks_to_trigger(self) -> Generator["ActionCallback", Any, None]:
        """
        Yields the callbacks to trigger in the order they should be triggered,
        while emptying the internal list.
        """
        # Convert to set and back to list to ensure uniqueness while preserving latest order
        unique_callbacks = list(set(self._callbacks_to_trigger))
        # Sort by original position to maintain discovery order
        unique_callbacks.sort(key=lambda x: self._callbacks_to_trigger.index(x))
        # empty the callbacks list
        self._callbacks_to_trigger = []
        while unique_callbacks:
            yield unique_callbacks.pop(0)

    def register_callbacks(self, match_context: "MatchContext"):
        raise NotImplementedError
