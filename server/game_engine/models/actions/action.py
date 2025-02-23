from functools import wraps

from config.logging import get_configured_logger
from dto.coordinates_dto import CoordinatesDto
from game_engine.models.actions.callbacks.action_callback import ActionCallback
from game_engine.models.actions.callbacks.action_callback_id import ActionCallBackId
from game_engine.models.actions.callbacks.callback_factory import get_callback
from game_engine.models.actions.hooks.action_hook import ActionHook
from game_engine.models.match_context import MatchContext

_logger = get_configured_logger(__name__)


class Action:
    """
    Base class for all actions
    """

    DEFAULT_MANA_COST = 0
    HOOKS: set[ActionHook] = set()
    CALLBACKS: set[ActionCallBackId] = set()

    def __init__(
        self,
        from_player1: bool,
        impacted_coords: CoordinatesDto,
    ):
        self.from_player1 = from_player1
        self.impacted_coords = impacted_coords
        self.mana_cost = self.DEFAULT_MANA_COST
        self.callbacks_to_trigger: set[ActionCallback] = set()

    def __repr__(self):
        return (
            f"<Action(from_player1={self.from_player1}, "
            f"impacted_coords={self.impacted_coords}, "
            f"mana_cost={self.mana_cost}, "
            f"callbacks_to_trigger={self.callbacks_to_trigger})>"
        )

    def to_dto(self):
        raise NotImplementedError

    def has_callbacks_to_trigger(self):
        return self.callbacks_to_trigger is not None and bool(self.callbacks_to_trigger)

    @staticmethod
    def create(*args, **kwargs) -> "Action":
        raise NotImplementedError

    @staticmethod
    def calculate(*args, **kwargs) -> set["Action"]:
        """
        Returns a list of instances of the class based on the given parameters.
        """
        raise NotImplementedError

    def trigger_hooks_and_check_callbacks(apply_action_func):
        @wraps(apply_action_func)
        def wrapper(self: "Action", match_context: MatchContext):
            self._trigger_hooks(match_context)

            apply_action_func(self, match_context)

            self._register_callbacks(match_context)

        return wrapper

    @trigger_hooks_and_check_callbacks
    def apply(self, match_context: MatchContext):
        """
        Applies the action on the given board.
        """
        raise NotImplementedError

    def _trigger_hooks(self, match_context: MatchContext):
        for hook in self.HOOKS:
            hook.trigger(self, match_context)

    def _register_callbacks(self, match_context: MatchContext):
        for callback_id in self.CALLBACKS:
            callback = get_callback(callback_id, self)
            if callback.can_be_triggered(match_context):
                self.callbacks_to_trigger.add(callback)
