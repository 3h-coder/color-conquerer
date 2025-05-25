import functools
from typing import TYPE_CHECKING

from config.logging import get_configured_logger
from game_engine.models.match.match_closure_info import EndingReason
from handlers.match_services.action_helpers.abstract.transient_turn_state_holder import (
    TransientTurnStateHolder,
)
from handlers.match_services.action_helpers.cell_selection_manager import (
    CellSelectionManager,
)
from handlers.match_services.action_helpers.cell_spawn_manager import CellSpawnManager
from handlers.match_services.action_helpers.common_action_manager import (
    CommonActionManager,
)
from handlers.match_services.action_helpers.spell_manager import SpellManager
from handlers.match_services.action_helpers.transient_turn_state import (
    TransientTurnState,
)
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
        self._logger = match_handler_unit.logger

        self.turn_state = self.match.turn_state
        # Dictionary storing all of the actions that happened during a match.
        # Key : turn number | Value : list of actions
        self.actions_per_turn: dict[int, list] = {}
        # Currently used to store the upper into the database
        self.actions_per_turn_serialized: dict[int, list[dict]] = {}

        self.common_action_manager = CommonActionManager(self)
        self.cell_selection_manager = CellSelectionManager(self)
        self.cell_spawn_manager = CellSpawnManager(self)
        self.spell_manager = SpellManager(self)

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
            self._logger.debug("Both died")
            self.match.end(EndingReason.DRAW)

        elif self.match_context.player1_is_dead():
            self._logger.debug("player 1 died")
            self.match.end(EndingReason.PLAYER_VICTORY, loser_id=player1.player_id)

        elif self.match_context.player2_is_dead():
            self._logger.debug("player 2 died")
            self.match.end(EndingReason.PLAYER_VICTORY, loser_id=player2.player_id)

    def reset_for_new_turn(self):
        """
        Performs all the cleanup and reset necessary for a fresh new turn.

        Meant to be used as a callback for the turn watcher service.
        """
        self.actions_per_turn[self.match_context.current_turn] = []
        self.actions_per_turn_serialized[self.match_context.current_turn] = []
        self.current_player = self.match.get_current_player()
        self.turn_state.reset_for_new_turn()
        self.set_player_as_idle()

    @_entry_point
    def handle_cell_selection(self, cell_row: int, cell_col: int):
        """
        Handles the cell selection from the current player.
        """
        self.cell_selection_manager.handle_cell_selection(cell_row, cell_col)

    @_entry_point
    def handle_spawn_toggle(self):
        """
        Handles the spawn toggling action, to either display the possible
        spawns or quit displaying it.
        """
        self.cell_spawn_manager.handle_spawn_toggle()

    @_entry_point
    def handle_spell_request(self, spell_id: int):
        """
        Handles the spell request of a player.
        """
        self.spell_manager.handle_spell_request(spell_id)
