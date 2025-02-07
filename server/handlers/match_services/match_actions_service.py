import functools
from typing import TYPE_CHECKING

from config.logging import get_configured_logger
from dto.server_only.match_action_dto import ActionType, MatchActionDto
from dto.server_only.match_closure_dto import EndingReason
from game_engine.models.player import Player
from handlers.match_services.action_calculator import ActionCalculator
from handlers.match_services.action_helpers.cell_selection_manager import (
    CellSelectionManager,
)
from handlers.match_services.action_helpers.cell_spawn_manager import CellSpawnManager
from handlers.match_services.action_helpers.error_messages import ErrorMessages
from handlers.match_services.action_helpers.player_mode import PlayerMode
from handlers.match_services.action_helpers.server_mode import ServerMode
from handlers.match_services.action_helpers.spell_manager import SpellManager
from handlers.match_services.action_helpers.transient_turn_state import (
    TransientTurnState,
)
from handlers.match_services.action_helpers.transient_turn_state_holder import (
    TransientTurnStateHolder,
)
from handlers.match_services.action_processor import ActionProcessor
from handlers.match_services.service_base import ServiceBase

if TYPE_CHECKING:
    from handlers.match_handler_unit import MatchHandlerUnit


class MatchActionsService(ServiceBase, TransientTurnStateHolder):
    """
    Helper class responsible for handling action requests from each players.
    The class handles both the action validation and action processing.
    """

    def __init__(self, match_handler_unit: "MatchHandlerUnit"):
        ServiceBase.__init__(self, match_handler_unit)
        TransientTurnStateHolder.__init__(self, TransientTurnState())
        self._logger = get_configured_logger(__name__)

        # region Match persistent fields

        self._board_array = self.match.match_context.board_array
        self.action_calculator = ActionCalculator(self.match_context)
        self._action_processor = ActionProcessor(self.match_context)

        # Dictionary storing all of the actions that happened during a match.
        # Key : turn number | Value : list of actions
        self.actions_per_turn: dict[int, list] = {}

        # endregion

        # region Turn persistent fields
        # ⚠️ Any field below is meant to be reset in the reset_for_new_turn method ⚠️

        # used to track all the cells that moved during the turn
        self.turn_state = self.match.turn_state

        self._cell_selection_manager = CellSelectionManager(self)
        self._cell_spawn_manager = CellSpawnManager(self)
        self._spell_manager = SpellManager(self)

    def _entry_point(func):
        """
        Decorator method to mark a method as en entry point for the service.

        This implies certain processing before and after the decorated method call
        such as checking for the game ending for example.
        """

        @functools.wraps(func)
        def wrapper(self: "MatchActionsService", *args, **kwargs):
            self.current_player = self.match.get_current_player()
            func(self, *args, **kwargs)
            self._end_match_if_game_over()

        return wrapper

    def _end_match_if_game_over(self):
        """
        Ends the match if at least one player dies.
        """
        player1 = self.match_context.player1
        player2 = self.match_context.player2

        if self.match_context.both_players_are_dead():
            self.match.end(EndingReason.DRAW)

        elif self.match_context.player1_is_dead():
            self.match.end(EndingReason.PLAYER_WON, loser_id=player1.player_id)

        elif self.match_context.player2_is_dead():
            self.match.end(EndingReason.PLAYER_WON, loser_id=player2.player_id)

    def reset_for_new_turn(self):
        """
        Performs all the cleanup and reset necessary for a fresh new turn.

        Meant to be used as a callback for the turn watcher service.
        """
        self.actions_per_turn[self.match_context.current_turn] = []
        self.turn_state.reset_for_new_turn()
        self.current_player = self.match.get_current_player()
        self.set_player_as_idle()

    @_entry_point
    def handle_cell_selection(self, cell_row: int, cell_col: int):
        """
        Handles the cell selection from the current player.
        """
        self._cell_selection_manager.handle_cell_selection(cell_row, cell_col)

    @_entry_point
    def handle_spawn_toggle(self):
        """
        Handles the spawn toggling action, to either display the possible
        spawns or quit displaying it.
        """
        self._cell_spawn_manager.handle_spawn_toggle()

    @_entry_point
    def handle_spell_request(self, spell_id: int):
        """
        Handles the spell request of a player.
        """
        self._spell_manager.handle_spell_request(spell_id)

    def validate_and_process_action(
        self, action: MatchActionDto, server_mode=ServerMode.SHOW_PROCESSED_ACTION
    ):
        """
        Validates the given action and processes it if it is valid.
        """
        if action not in self.get_possible_actions():
            self._logger.error(
                f"The following action was not registered in the possible actions : {action}"
            )
            self.set_error_message(ErrorMessages.INVALID_ACTION)
            return

        if action.manaCost > self.current_player.resources.current_mp:
            self.set_error_message(ErrorMessages.NOT_ENOUGH_MANA)
            return

        self._process_action(action, server_mode)

    def _process_action(
        self,
        action: MatchActionDto,
        server_mode=ServerMode.SHOW_PROCESSED_ACTION,
    ):
        """
        Processes all of the given actions, setting the associate fields along the way.

        Note : Action validation should be done before calling this method.
        """
        self.set_server_mode(
            server_mode
            if server_mode != ServerMode.SHOW_POSSIBLE_ACTIONS
            else ServerMode.SHOW_PROCESSED_ACTION
        )
        processed_action = self._action_processor.process_action(action)
        if processed_action is None:
            self.set_player_as_idle()
            self.set_error_message(ErrorMessages.INVALID_ACTION)
            return

        self.set_error_message("")

        self.set_processed_action(processed_action)
        self._register_processed_action(processed_action)
        self._calculate_post_processing_possible_actions()

    def _register_processed_action(self, action: MatchActionDto):
        """
        Adds a processed action to the turn and match actions fields.
        """
        current_turn = self.match_context.current_turn
        if current_turn not in self.actions_per_turn:
            self.actions_per_turn[current_turn] = []

        self.actions_per_turn[current_turn].append(action)

        cell_id = action.cellId
        if action.type == ActionType.CELL_MOVE:
            self.turn_state.movements.append(cell_id)

        elif action.type == ActionType.CELL_ATTACK:
            self.turn_state.attacks.append(cell_id)

    def _calculate_post_processing_possible_actions(self):
        """
        Meant to be called right after action processing.
        """
        self.set_transient_board_array(None)
        server_mode = self.get_server_mode()

        if server_mode != ServerMode.SHOW_PROCESSED_AND_POSSIBLE_ACTIONS:
            return

        player_mode = self.get_player_mode()
        if player_mode == PlayerMode.CELL_SPAWN:
            self._cell_spawn_manager.find_possible_spawns(update_server_mode=False)
