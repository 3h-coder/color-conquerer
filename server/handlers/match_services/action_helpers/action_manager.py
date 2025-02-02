import functools
from typing import TYPE_CHECKING

from dto.server_only.match_action_dto import MatchActionDto
from handlers.match_services.action_helpers.transient_turn_state_holder import (
    TransientTurnStateHolder,
)
from utils.board_utils import copy_board

if TYPE_CHECKING:
    from handlers.match_services.match_actions_service2 import MatchActionsService2
    from handlers.match_services.action_helpers.transient_turn_state import (
        TransientTurnState,
    )


class ActionManager(TransientTurnStateHolder):
    """
    Base class for all managers.

    In this package's context, a manager is a helper class to handle a use case
    within the action service.
    """

    def __init__(self, match_actions_service: "MatchActionsService2"):
        super().__init__(self, match_actions_service.transient_turn_state)
        self._match_actions_service = match_actions_service
        self._board_array = match_actions_service._board_array

    def send_response_to_client(self):
        self._match_actions_service.send_response_to_client()

    def get_current_player(self):
        return self._match_actions_service.current_player

    def initialize_transient_board(func):
        """
        Decorator method that ensures the transient board is properly initialized.

        To be wrapped around any method that uses the transient board.
        """

        @functools.wraps(func)
        def wrapper(self: "ActionManager", *args, **kwargs):
            if self.get_transient_board_array() is None:
                self.set_transient_board_array(copy_board(self._board_array))
            return func(self, *args, **kwargs)

        return wrapper
