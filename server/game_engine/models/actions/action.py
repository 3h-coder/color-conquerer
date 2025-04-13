from functools import wraps

from game_engine.models.actions.callbacks.action_callback_id import ActionCallBackId
from game_engine.models.actions.callbacks.callback_factory import get_callback
from game_engine.models.actions.callbacks.with_callbacks import WithCallbacks
from game_engine.models.actions.hooks.action_hook import ActionHook
from game_engine.models.dtos.action_metadata import ActionMedatata
from game_engine.models.dtos.coordinates import Coordinates
from game_engine.models.match_context import MatchContext


class Action(WithCallbacks):
    """
    Base class for all actions
    """

    DEFAULT_MANA_COST = 0
    HOOKS: set[ActionHook] = set()
    CALLBACKS: set[ActionCallBackId] = set()

    def __init__(
        self,
        from_player1: bool,
        impacted_coords: Coordinates,
    ):
        super().__init__()
        self.from_player1 = from_player1
        self.mana_cost = self.DEFAULT_MANA_COST
        self.metadata: ActionMedatata = ActionMedatata.get_default()
        self.metadata.impacted_coords = impacted_coords

    def __repr__(self):
        return (
            f"<Action(from_player1={self.from_player1}, "
            f"mana_cost={self.mana_cost}, "
            f"metadata={self.metadata}, "
            f"callbacks_to_trigger={self._callbacks_to_trigger})>"
        )

    def to_dto(self):
        raise NotImplementedError

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

            self.register_callbacks(match_context)

        return wrapper

    @trigger_hooks_and_check_callbacks
    def apply(self, match_context: MatchContext):
        """
        Applies the action on the given board.
        """
        raise NotImplementedError

    def register_callbacks(self, match_context: MatchContext):
        for callback_id in self.CALLBACKS:
            callback = get_callback(callback_id, self)
            if callback.can_be_triggered(match_context):
                self._callbacks_to_trigger.append(callback)

    def _trigger_hooks(self, match_context: MatchContext):
        for hook in self.HOOKS:
            hook.trigger(self, match_context)
