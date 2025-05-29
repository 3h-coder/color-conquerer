from functools import wraps
from typing import TYPE_CHECKING, Any, Type

from config.logging import get_configured_logger
from dto.actions.action_callback_dto import ActionCallbackDto
from dto.game_state.game_context_dto import GameContextDto
from game_engine.models.actions.abstract.with_callbacks import WithCallbacks
from game_engine.models.actions.callbacks.action_callback_id import ActionCallBackId
from game_engine.models.actions.callbacks.callback_factory import get_callback
from game_engine.models.dtos.coordinates import Coordinates
from game_engine.models.game_board import GameBoard
from game_engine.models.match.match_context import MatchContext
from game_engine.models.player.player_resources import PlayerResources
from game_engine.models.spells.abstract.spell import Spell

if TYPE_CHECKING:
    from game_engine.models.actions.abstract.action import Action


class ActionCallbackMeta(type):
    """
    Metaclass to automatically wrap the 'trigger' method of ActionCallback subclasses
    with check_for_callbacks and update_game_board_and_player_resources.
    """

    def __new__(
        mcs: Type[type], name: str, bases: tuple[type, ...], namespace: dict[str, Any]
    ):
        TRIGGER_METHOD_NAME = "trigger"
        trigger_func = namespace.get(TRIGGER_METHOD_NAME)
        if trigger_func is not None and callable(trigger_func):

            @wraps(trigger_func)
            def wrapped_trigger(self: "ActionCallback", match_context: MatchContext):
                """
                Wraps the trigger method to ensure that callbacks are checked
                and game board/player resources are updated after the action is triggered.
                """
                trigger_func(self, match_context)

                self.check_for_callbacks(match_context)
                self.update_game_board_and_player_resources(match_context)

            namespace[TRIGGER_METHOD_NAME] = wrapped_trigger
        return super().__new__(mcs, name, bases, namespace)


class ActionCallback(WithCallbacks, metaclass=ActionCallbackMeta):
    """
    Defines an action that is indirectly triggered by another, and therefore
    should be called after an action is performed.
    """

    ID = ActionCallBackId.NONE
    SPELL_CAUSE: type[Spell] | None = None

    def __init__(
        self, parent_action: "Action", parent_callback: "ActionCallback" = None
    ):
        super().__init__()
        self.parent_action = parent_action
        self.parent_callback = parent_callback
        self.updated_game_board: GameBoard | None = None
        self.updated_player_resources: (
            tuple[PlayerResources, PlayerResources] | None
        ) = None
        self.deaths: list[Coordinates] = []
        self.can_trigger_callbacks = True

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
            parentCallbackId=(
                self.parent_callback.ID
                if self.parent_callback
                else ActionCallBackId.NONE
            ),
            spellCause=(
                self.SPELL_CAUSE.to_partial_dto()
                if self.SPELL_CAUSE is not None
                else None
            ),
            deaths=[coord.to_dto() for coord in self.deaths],
            impactedCoords=self.parent_action.metadata.impacted_coords.to_dto(),
            updatedGameContext=GameContextDto.from_action_callback(self, for_player1),
        )

    def can_be_triggered(self, match_context: MatchContext):
        raise NotImplementedError

    def check_for_callbacks(self, match_context: MatchContext):
        """
        Registers eventual callbacks
        after the callback has triggered.
        """
        if self.can_trigger_callbacks:
            self.register_callbacks(match_context)

    def update_game_board_and_player_resources(self, match_context: MatchContext):
        """
        Sets the updated_game_board field after
        triggering the callback.
        """
        self.updated_game_board = match_context.game_board.clone()
        self.updated_player_resources = match_context.get_both_players_resources()

    def trigger(self, match_context: MatchContext):
        raise NotImplementedError
