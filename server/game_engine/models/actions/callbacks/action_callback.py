from functools import wraps
from typing import TYPE_CHECKING

from dto.action_callback_dto import ActionCallbackDto
from dto.game_context_dto import GameContextDto
from game_engine.models.actions.callbacks.action_callback_id import ActionCallBackId
from game_engine.models.game_board import GameBoard
from game_engine.models.match_context import MatchContext
from game_engine.models.player_resources import PlayerResources

if TYPE_CHECKING:
    from game_engine.models.actions.action import Action


class ActionCallback:
    """
    Defines an action that is indirectly triggered by another, and therefore
    should be called after an action is performed.
    """

    ID = ActionCallBackId.NONE

    def __init__(self, parent_action: "Action"):
        self.parent_action = parent_action
        self.updated_game_board: GameBoard | None = None
        self.updated_player_resources: (
            tuple[PlayerResources, PlayerResources] | None
        ) = None

    def __eq__(self, other):
        return (
            isinstance(other, ActionCallback)
            and self.ID == other.ID
            and self.parent_action == other.parent_action
        )

    def __hash__(self):
        return hash((self.ID, self.parent_action))

    def __repr__(self):
        return f"<Callback : {self.ID.name}>"

    def to_dto(self, for_player1: bool):
        return ActionCallbackDto(
            id=self.ID,
            parentAction=self.parent_action.to_dto(),
            updatedGameContext=GameContextDto.from_action_callback(self, for_player1),
        )

    def can_be_triggered(self, match_context: MatchContext):
        raise NotImplementedError

    def update_game_board_and_player_resources(trigger_func):
        """
        Decorator to automatically set the updated_game_board field after
        triggering the callback.
        """

        @wraps(trigger_func)
        def wrapper(self: "ActionCallback", match_context: MatchContext):
            trigger_func(self, match_context)

            self.updated_game_board = match_context.game_board.clone()
            self.updated_player_resources = match_context.get_both_player_resources()

        return wrapper

    @update_game_board_and_player_resources
    def trigger(self, match_context: MatchContext):
        raise NotImplementedError
