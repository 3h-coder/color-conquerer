from typing import TYPE_CHECKING
from ai.strategy.ai_decision_brain import AIDecisionBrain
from game_engine.models.actions.cell_spawn import CellSpawn
from game_engine.models.actions.cell_attack import CellAttack
from game_engine.models.actions.cell_movement import CellMovement
from game_engine.models.actions.spell_casting import SpellCasting
from config.logging import get_configured_logger

from ai.config.ai_config import (
    DELAY_BEFORE_PASSING_TURN_IN_S,
    DELAY_IN_BETWEEN_CLICKS_IN_S,
    MAX_ACTIONS_PER_TURN,
    THINKING_DELAY_MIN_IN_S,
    THINKING_DELAY_MAX_IN_S,
    TURN_STARTING_DELAY_IN_S,
)
import random

if TYPE_CHECKING:
    from handlers.match_handler_unit import MatchHandlerUnit


class AIPlayer:
    """
    Represents an AI-controlled player that makes automated decisions.
    """

    def __init__(self, match_handler_unit: "MatchHandlerUnit", player_id: str):
        self._match = match_handler_unit
        self.player_id = player_id
        self._logger = get_configured_logger(__name__)

        # Determine if AI is player 1 or player 2
        self._ai_is_player1 = (
            match_handler_unit.match_context.player1.player_id == player_id
        )

        # Initialize the decision brain
        self._brain = AIDecisionBrain(match_handler_unit, self._ai_is_player1)

    def take_turn(self):
        """
        Called when it's the AI's turn.
        Iteratively evaluates the board and performs actions until the turn ends
        or no more actions are possible.
        """
        self._logger.info(f"AI ({self.player_id}) starting turn...")
        self._sleep(TURN_STARTING_DELAY_IN_S)

        self._perform_action_loop()

        if self._is_my_turn():
            self._logger.info("AI turn completed, passing turn.")
            # Wait a little so the player can see the final action before
            # the turn swap
            self._sleep(DELAY_BEFORE_PASSING_TURN_IN_S)
            self._match.force_turn_swap()
        else:
            self._logger.info("AI turn was terminated externally or completed.")

    def _perform_action_loop(self):
        """
        Core action loop: repeatedly decides and executes actions until
        no more are available, one is rejected, or limits are reached.
        """
        for _ in range(MAX_ACTIONS_PER_TURN):
            if not self._is_my_turn():
                return

            action = self._brain.decide_next_best_action()
            if not action:
                self._logger.info("AI has no more valid actions to take.")
                return

            if not self._execute_action(action):
                self._logger.error(
                    f"AI action {type(action).__name__} was rejected by the game engine. Ending turn."
                )
                return

            delay = random.uniform(THINKING_DELAY_MIN_IN_S, THINKING_DELAY_MAX_IN_S)
            self._sleep(delay)

        self._logger.warning(f"AI reached max actions limit ({MAX_ACTIONS_PER_TURN})")

    def _is_my_turn(self) -> bool:
        """Checks if the match is still ongoing and it is currently the AI's turn."""
        if not self._match.is_ongoing():
            return False

        return self._match.get_current_player().player_id == self.player_id

    def _execute_action(self, action) -> bool:
        """
        Dispatches action execution based on target action type.
        Returns True if the action sequence was triggered without immediate error.
        """
        # Reset any previous transient turn state (selected cell, player mode, errors, etc.)
        # This ensures a clean state for each action attempt, preventing stale cell
        # selections from leaking between attempts and causing cascading errors.
        self._match._match_actions_service.cell_selection_manager.set_player_as_idle()

        if isinstance(action, CellSpawn):
            coords = action.metadata.impacted_coords
            self._logger.debug(f"AI executing Spawn at {coords}")

            self._match.handle_spawn_button()
            self._sleep(DELAY_IN_BETWEEN_CLICKS_IN_S)
            self._match.handle_cell_selection(coords.row_index, coords.column_index)

        elif isinstance(action, SpellCasting):
            spell_id = action.spell.ID
            coords = action.metadata.impacted_coords
            self._logger.debug(f"AI casting {action.spell.NAME} at {coords}")

            self._match.handle_spell_button(spell_id)
            self._sleep(DELAY_IN_BETWEEN_CLICKS_IN_S)
            self._match.handle_cell_selection(coords.row_index, coords.column_index)

        elif isinstance(action, (CellAttack, CellMovement)):
            origin = action.metadata.originating_coords
            target = action.metadata.impacted_coords

            action_name = "Attack" if isinstance(action, CellAttack) else "Move"
            self._logger.debug(f"AI executing {action_name}: {origin} -> {target}")

            self._match.handle_cell_selection(origin.row_index, origin.column_index)
            self._sleep(DELAY_IN_BETWEEN_CLICKS_IN_S)
            self._match.handle_cell_selection(target.row_index, target.column_index)

        else:
            self._logger.warning(
                f"AI Brain returned unknown action type: {type(action)}"
            )
            return False

        # return False if an error occurred during the sequence
        return not self._has_error()

    def _has_error(self) -> bool:
        """Checks if the match manager has a pending error message."""
        error = (
            self._match._match_actions_service.cell_selection_manager.get_error_message()
        )
        if error:
            self._logger.error(f"Engine reported error during AI action click: {error}")
            return True
        return False

    def _sleep(self, seconds: float):
        """Utility method to sleep using the server's socketio (non-blocking)."""
        self._match.server.socketio.sleep(seconds)
