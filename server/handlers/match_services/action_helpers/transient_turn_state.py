from typing import Any

from game_engine.models.actions.action import Action
from game_engine.models.actions.callbacks.action_callback import ActionCallback
from game_engine.models.cell.cell import Cell
from game_engine.models.game_board import GameBoard
from game_engine.models.spells.abstract.spell import Spell
from handlers.match_services.action_helpers.enums.player_mode import PlayerMode
from handlers.match_services.action_helpers.enums.server_mode import ServerMode


class TransientTurnState:
    """
    Represents the transient state of a turn, storing and manipulating
    data relative to both the player and the server.

    Note : An instance of this class is meant to be reset regularly and
    at the end/beginning of each turn.
    """

    def __init__(self):
        # Used to confirm whether an action can be done or not
        self.possible_actions: set[Action] = set()
        self.possible_actions_metadata: Any = None
        # Actions that have been validated and applied,
        # overridden each time a set of action is processed
        self.processed_action: Action | None = None
        self.triggered_callbacks: set[ActionCallback] = set()
        self.player_mode = PlayerMode.IDLE
        self.server_mode = ServerMode.SHOW_POSSIBLE_ACTIONS
        # Board copy to save and send to the client the transient states
        # resulting from the possible actions.
        self.transient_game_bard: GameBoard | None = None
        # Applicable when the player mode is OWN_CELL_SELECTED
        self.selected_cell: Cell | None = None
        # Applicable when the player mode is SPELL_SELECTED
        self.selected_spell: Spell | None = None
        # Message to the player when their request is invalid
        self.error_msg: str = ""

    def reset(self):
        self.player_mode = PlayerMode.IDLE
        self.server_mode = ServerMode.SHOW_POSSIBLE_ACTIONS

        self.possible_actions = set()
        self.possible_actions_metadata = None
        self.processed_action = None
        self.triggered_callbacks = set()

        self.transient_game_bard = None
        self.selected_cell = None
        self.selected_spell = None

        self.error_msg = ""

    def set_possible_actions(self, actions: set[Action], update_server_mode=True):
        """
        Stores all of the possible actions and sets the server mode accordingly.
        """
        if update_server_mode:
            self.server_mode = ServerMode.SHOW_POSSIBLE_ACTIONS
        self.possible_actions = actions
