from game_engine.models.actions.action import Action
from game_engine.models.cell.cell import Cell
from game_engine.models.spells.spell import Spell
from handlers.match_services.action_helpers.player_mode import PlayerMode
from handlers.match_services.action_helpers.server_mode import ServerMode
from handlers.match_services.action_helpers.transient_turn_state import (
    TransientTurnState,
)


class TransientTurnStateHolder:
    """
    Indicates that this class contains a TransientTurnState instance,
    and defines helper methods to access and modify the subsequent fields.
    """

    def __init__(self, transient_turn_state: TransientTurnState | None = None):
        if transient_turn_state is None:
            transient_turn_state = TransientTurnState()
        self.transient_turn_state = transient_turn_state

    def set_player_as_idle(self):
        """
        Resets all the temporary fields used to store the state of the current player's action.

        This is an effective reset of a player's action state.

        Note : This will also reset any error message.
        """
        self.transient_turn_state.reset()

    def get_possible_actions(self):
        return self.transient_turn_state.possible_actions

    def set_possible_actions(self, actions: set[Action], update_server_mode=True):
        self.transient_turn_state.set_possible_actions(actions, update_server_mode)

    def get_processed_action(self):
        return self.transient_turn_state.processed_action

    def set_processed_action(self, action: Action):
        self.transient_turn_state.processed_action = action

    def get_player_mode(self):
        return self.transient_turn_state.player_mode

    def set_player_mode(self, player_mode: PlayerMode):
        self.transient_turn_state.player_mode = player_mode

    def get_server_mode(self):
        return self.transient_turn_state.server_mode

    def set_server_mode(self, server_mode: ServerMode):
        self.transient_turn_state.server_mode = server_mode

    def get_transient_board_array(self):
        return self.transient_turn_state.transient_board_array

    def set_transient_board_array(self, new_board_array):
        self.transient_turn_state.transient_board_array = new_board_array

    def get_selected_cell(self):
        return self.transient_turn_state.selected_cell

    def set_selected_cell(self, cell: Cell):
        self.transient_turn_state.selected_cell = cell

    def get_selected_spell(self):
        return self.transient_turn_state.selected_spell

    def set_selected_spell(self, spell: Spell):
        self.transient_turn_state.selected_spell = spell

    def get_error_message(self):
        return self.transient_turn_state.error_msg

    def set_error_message(self, error_msg: str):
        self.transient_turn_state.error_msg = error_msg
