from functools import wraps

from config.logging import get_configured_logger
from dto.coordinates_dto import CoordinatesDto
from game_engine.models.actions.callbacks.action_callback import ActionCallback
from game_engine.models.actions.callbacks.action_callback_id import ActionCallBackId
from game_engine.models.actions.callbacks.callback_factory import get_callback
from game_engine.models.match_context import MatchContext

_logger = get_configured_logger(__name__)


class Action:
    """
    Base class for all actions
    """

    DEFAULT_MANA_COST = 0
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
            f"mana_cost={self.mana_cost})>"
        )

    def to_dto(self):
        raise NotImplementedError

    def get_callbacks_dto(self):
        return [callback.to_dto() for callback in self.callbacks_to_trigger]

    @staticmethod
    def create(*args, **kwargs) -> "Action":
        raise NotImplementedError

    @staticmethod
    def calculate(*args, **kwargs) -> set["Action"]:
        """
        Returns a list of instances of the class based on the given parameters.
        """
        raise NotImplementedError

    def check_callbacks(apply_action_func):
        @wraps(apply_action_func)
        def wrapper(self: "Action", match_context: MatchContext):
            apply_action_func(self, match_context)

            for callback_id in self.CALLBACKS:
                callback = get_callback(callback_id, self)
                if callback.can_be_triggered(match_context):
                    _logger.debug(f"Adding the following callback {callback.ID}")
                    self.callbacks_to_trigger.add(callback)

        return wrapper

    @check_callbacks
    def apply(self, match_context: MatchContext):
        """
        Applies the action on the given board.
        """
        raise NotImplementedError
