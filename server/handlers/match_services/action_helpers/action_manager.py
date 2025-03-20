import functools
from typing import TYPE_CHECKING

from config.logging import get_configured_logger
from dto.actions.possible_actions_dto import PossibleActionsDto
from dto.actions.processed_action_dto import ProcessedActionDto
from game_engine.models.actions.action import Action
from game_engine.models.actions.callbacks.action_callback import ActionCallback
from handlers.match_services.action_helpers.player_mode import PlayerMode
from handlers.match_services.action_helpers.server_mode import ServerMode
from handlers.match_services.action_helpers.transient_turn_state_holder import (
    TransientTurnStateHolder,
)
from handlers.match_services.client_notifications import (
    notify_action_error,
    notify_possible_actions,
    notify_processed_action,
    notify_triggered_callback,
)

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
        self._game_board = match_actions_service._game_board
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
            if self.get_transient_game_board() is None:
                self.set_transient_game_board(self._game_board.clone_as_transient())
            return func(self, *args, **kwargs)

        return wrapper

    def entry_point(with_turn_state_reset=False):
        """
        Decorator used to gracefully handle action entry points.

        This will notify both clients once the action is processed and will also
        handle potential callbacks triggered by the processed action, notifying them
        along the way.
        """

        def decorator(func):
            @functools.wraps(func)
            def wrapper(self: "ActionManager", *args, **kwargs):
                # Action processing function
                func(self, *args, **kwargs)

                # Notify the clients for them to render/animate it
                self.send_response_to_clients()

                for callback in self.trigger_callbacks():
                    self.send_callback_to_clients(callback)

                if (
                    with_turn_state_reset
                    and self.get_server_mode() == ServerMode.SHOW_PROCESSED_ACTION
                ):
                    self.set_player_as_idle()

            return wrapper

        # If "func" is passed directly (without parentheses), return the decorator applied to func
        if callable(with_turn_state_reset):
            # Treat "with_turn_state_reset" as the function
            return decorator(with_turn_state_reset)
        # Otherwise, return the decorator normally
        return decorator

    def validate_and_process_action(
        self, action: Action, server_mode=ServerMode.SHOW_PROCESSED_ACTION
    ):
        self._match_actions_service.validate_and_process_action(action, server_mode)

    def trigger_callbacks(self):
        return self._match_actions_service.trigger_callbacks()

    def send_response_to_clients(self):
        """
        Crucial method.

        Let's the client know the server's response to the player's request allowing it to render
        subsequent animations properly.
        """
        if error_msg := self.get_error_message():
            self._logger.debug(f"Sending to the client the error message : {error_msg}")
            notify_action_error(error_msg)
            return

        current_player = self.get_current_player()
        player_mode = self.get_player_mode()
        server_mode = self.get_server_mode()
        processed_action = self.get_processed_action()

        # Send the possible actions
        if server_mode == ServerMode.SHOW_POSSIBLE_ACTIONS:
            notify_possible_actions(
                PossibleActionsDto(
                    player_mode,
                    self._get_client_friendly_transient_board(
                        current_player.is_player_1
                    ),
                )
            )
            return

        processed_action_dto_1 = self._get_processed_action_dto(
            player_mode, processed_action, True
        )
        processed_action_dto_2 = self._get_processed_action_dto(
            player_mode, processed_action, False
        )
        player1_room, player2_room = self._match.get_individual_player_rooms()
        # Send the processed action
        if server_mode == ServerMode.SHOW_PROCESSED_ACTION:
            notify_processed_action(
                processed_action_dto_1,
                processed_action_dto_2,
                player1_room,
                player2_room,
                self._match.lock,
            )
            return

        # Send both the processed action and further possible actions (through the overriding transient board)
        if server_mode == ServerMode.SHOW_PROCESSED_AND_POSSIBLE_ACTIONS:
            if current_player.is_player_1:
                processed_action_dto_1.overridingTransientBoard = (
                    self._get_client_friendly_transient_board(for_player1=True)
                )
            else:
                processed_action_dto_2.overridingTransientBoard = (
                    self._get_client_friendly_transient_board(for_player1=False)
                )

            notify_processed_action(
                processed_action_dto_1,
                processed_action_dto_2,
                player1_room,
                player2_room,
                self._match.lock,
            )

    def send_callback_to_clients(self, callback: ActionCallback):
        action_callback_dto1 = callback.to_dto(for_player1=True)
        action_callback_dto2 = callback.to_dto(for_player1=False)
        player1_room, player2_room = self._match.get_individual_player_rooms()
        server_mode = self.get_server_mode()
        current_player = self.get_current_player()

        if server_mode == ServerMode.SHOW_PROCESSED_AND_POSSIBLE_ACTIONS:
            if current_player.is_player_1:
                action_callback_dto1.updatedGameContext.gameBoard = (
                    self._get_client_friendly_transient_board(for_player1=True)
                )
            else:
                action_callback_dto2.updatedGameContext.gameBoard = (
                    self._get_client_friendly_transient_board(for_player1=False)
                )

        notify_triggered_callback(
            action_callback_dto1,
            action_callback_dto2,
            player1_room,
            player2_room,
            self._match.lock,
        )

    def _get_processed_action_dto(
        self, player_mode: PlayerMode, processed_action: Action, for_player1: bool
    ):
        return ProcessedActionDto(
            processedAction=processed_action.to_dto(),
            playerMode=player_mode,
            updatedGameContext=self._match.get_game_context_dto(for_player1),
            overridingTransientBoard=None,
        )

    def _get_client_friendly_transient_board(self, for_player1: bool):
        transient_game_board = self.get_transient_game_board()
        return (
            transient_game_board.to_dto(for_player1)
            if transient_game_board
            else self._game_board.to_dto(for_player1)
        )
