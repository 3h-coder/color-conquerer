from dataclasses import dataclass
from dto.server_only.match_action_dto import MatchActionDto
from game_engine.models.cell import Cell
from game_engine.spells.spell import Spell
from handlers.match_services.action_helpers.player_mode import PlayerMode
from handlers.match_services.action_helpers.server_mode import ServerMode


@dataclass
class TransientTurnState:
    """
    Represents the transient state of a turn, storing and manipulating
    data relative to both the player and the server.

    Note : An instance of this class is meant to be reset regularly and
    at the end/beginning of each turn.
    """

    # Used to confirm whether an action can be done or not
    possible_actions: set[MatchActionDto] = set()
    # Actions that have been validated and applied,
    # overridden each time a set of action is processed
    processed_action: MatchActionDto | None = None
    player_mode = PlayerMode.IDLE
    server_mode = ServerMode.SHOW_POSSIBLE_ACTIONS
    # Board copy to save and send to the client the transient states
    # resulting from the possible actions.
    transient_board_array: list[list[Cell]] | None = None
    # Applicable when the player mode is OWN_CELL_SELECTED
    selected_cell: Cell | None = None
    # Applicable when the player mode is SPELL_SELECTED
    selected_spell: Spell | None = None
    # Message to the player when their request is invalid
    error_msg: str = ""

    def reset(self):
        self.player_mode = PlayerMode.IDLE
        self.server_mode = ServerMode.SHOW_POSSIBLE_ACTIONS
        self.possible_actions = set()
        self.processed_action = None
        self.transient_board_array = None
        self.selected_cell = None
        self.selected_spell = None
        self.error_msg = ""

    def set_possible_actions(
        self, actions: set[MatchActionDto], update_server_mode=True
    ):
        """
        Stores all of the possible actions and sets the server mode accordingly.
        """
        if update_server_mode:
            self.server_mode = ServerMode.SHOW_POSSIBLE_ACTIONS
        self.possible_actions = actions

    def set_selected_cell(self, cell: Cell):
        self.player_mode = PlayerMode.OWN_CELL_SELECTED
        self.selected_cell = cell
        transient_cell: Cell = self.transient_board_array[cell.row_index][
            cell.column_index
        ]
        transient_cell.set_selected()
