from typing import TYPE_CHECKING
from ai.strategy.ai_decision_brain import AIDecisionBrain
from game_engine.models.actions.cell_spawn import CellSpawn
from game_engine.models.actions.cell_attack import CellAttack
from game_engine.models.actions.cell_movement import CellMovement
from config.logging import get_configured_logger

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
        Iteratively evaluates the board and performs actions until the turn ends or no more actions are possible.
        """
        self._logger.info(f"AI ({self.player_id}) starting turn...")

        while self._is_my_turn():
            # 1. Decide on an action (internally evaluates board)
            action = self._brain.decide_next_best_action()

            if not action:
                # No more actions the AI wants to take
                self._logger.info("AI has no more actions to take.")
                break

            # 2. Execute the action
            self._execute_action(action)

            # 4. Check if turn ended during execution
            if not self._is_my_turn():
                break

            # 5. Natural delay between actions
            self._sleep(0.5)

        # Final check: if it's still AI's turn, pass it
        if self._is_my_turn():
            self._logger.info("AI turn completed, passing turn.")
            self._match.force_turn_swap()
        else:
            self._logger.info("AI turn was terminated externally (e.g., timeout).")

    def _is_my_turn(self) -> bool:
        """Checks if the match is still ongoing and it is currently the AI's turn."""
        if not self._match.is_ongoing():
            return False

        return self._match.get_current_player().player_id == self.player_id

    def _execute_action(self, action):
        """Dispatches action execution based on target action type."""
        if isinstance(action, CellSpawn):
            coords = action.metadata.impacted_coords
            self._logger.info(f"AI executing Spawn at {coords}")

            # Simulate UI interaction sequence
            self._match.handle_spawn_button()
            self._sleep(0.6)  # Simulate delay for button press
            self._match.handle_cell_selection(coords.row_index, coords.column_index)

        elif isinstance(action, (CellAttack, CellMovement)):
            origin = action.metadata.originating_coords
            target = action.metadata.impacted_coords
            action_name = "Attack" if isinstance(action, CellAttack) else "Move"
            self._logger.info(f"AI executing {action_name} from {origin} to {target}")

            # Simulate UI interaction sequence: Select cell then select target
            self._match.handle_cell_selection(origin.row_index, origin.column_index)
            self._sleep(0.6)
            self._match.handle_cell_selection(target.row_index, target.column_index)

        else:
            self._logger.warning(
                f"AI Brain returned unknown action type: {type(action)}"
            )

    def _sleep(self, seconds: float):
        """Utility method to sleep using the server's socketio (non-blocking)."""
        self._match.server.socketio.sleep(seconds)
