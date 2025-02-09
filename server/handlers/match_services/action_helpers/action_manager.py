import functools
from typing import TYPE_CHECKING

from config.logging import get_configured_logger
from dto.possible_actions_dto import PossibleActionsDto
from dto.processed_action_dto import ProcessedActionDto
from game_engine.models.actions.action import Action
from handlers.match_services.action_helpers.player_mode import PlayerMode
from handlers.match_services.action_helpers.server_mode import ServerMode
from handlers.match_services.action_helpers.transient_turn_state_holder import (
    TransientTurnStateHolder,
)
from handlers.match_services.client_notifications import (
    notify_action_error,
    notify_possible_actions,
    notify_processed_action,
)
from utils.board_utils import copy_board, to_client_board_dto

if TYPE_CHECKING:
    from handlers.match_services.match_actions_service import MatchActionsService


class ActionManager(TransientTurnStateHolder):
    """
    Base class for all managers.

    In this package's context, a manager is a helper class to handle a use case
    within the action service.
    """

    def __init__(self, match_actions_service: "MatchActionsService"):
        super().__init__(match_actions_service.transient_turn_state)
        self._match_actions_service = match_actions_service
        self._board_array = match_actions_service._board_array
        self._match = match_actions_service.match
        self._room_id = match_actions_service.match.match_context.room_id
        self._logger = get_configured_logger(__name__)

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

    def validate_and_process_action(
        self, action: Action, server_mode=ServerMode.SHOW_PROCESSED_ACTION
    ):
        self._match_actions_service.validate_and_process_action(action, server_mode)

    def send_response_to_client(self):
        """
        Crucial method.

        Let's the client know the server's response to the player's request allowing it to render
        subsequent animations properly.
        """
        if error_msg := self.get_error_message():
            self._logger.debug(f"Sending to the client the error message : {error_msg}")
            notify_action_error(error_msg)
            return

        player_mode = self.get_player_mode()
        server_mode = self.get_server_mode()
        processed_action = self.get_processed_action()

        # Send the possible actions
        if server_mode == ServerMode.SHOW_POSSIBLE_ACTIONS:
            notify_possible_actions(
                PossibleActionsDto(
                    player_mode,
                    self._get_client_friendly_transient_board(),
                )
            )
            return

        processed_action_dto = self._get_processed_action_dto(
            player_mode, processed_action
        )
        # Send the processed action
        if server_mode == ServerMode.SHOW_PROCESSED_ACTION:
            notify_processed_action(
                processed_action_dto,
                self._room_id,
            )
            return

        # Send both the processed action and further possible actions (through the overriding transient board)
        if server_mode == ServerMode.SHOW_PROCESSED_AND_POSSIBLE_ACTIONS:
            processed_action_dto.overridingTransientBoard = (
                self._get_client_friendly_transient_board()
            )

            notify_processed_action(
                processed_action_dto,
                self._room_id,
            )

    def _get_processed_action_dto(
        self, player_mode: PlayerMode, processed_action: Action
    ):
        return ProcessedActionDto(
            processedAction=processed_action.to_dto(),
            playerMode=player_mode,
            updatedTurnInfo=self._match.get_turn_context_dto(),
            overridingTransientBoard=None,
        )

    def _get_client_friendly_transient_board(self):
        transient_board_array = self.get_transient_board_array()
        return (
            to_client_board_dto(transient_board_array)
            if transient_board_array
            else to_client_board_dto(self._board_array)
        )
