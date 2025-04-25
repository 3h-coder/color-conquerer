from typing import TYPE_CHECKING

from config.logging import get_configured_logger
from game_engine.action_calculation import get_possible_movements_and_attacks
from game_engine.models.actions.cell_attack import CellAttack
from game_engine.models.actions.cell_movement import CellMovement
from game_engine.models.actions.cell_spawn import CellSpawn
from game_engine.models.actions.spell_casting import SpellCasting
from game_engine.models.cell.cell import Cell
from handlers.match_services.action_helpers.abstract.action_manager import ActionManager
from handlers.match_services.action_helpers.enums.error_messages import ErrorMessages
from handlers.match_services.action_helpers.enums.player_mode import PlayerMode
from handlers.match_services.action_helpers.enums.server_mode import ServerMode

if TYPE_CHECKING:
    from handlers.match_services.match_actions_service import MatchActionsService


class CellSelectionManager(ActionManager):
    """
    Helper class to handle cell selection from the current player.

    Selecting a cell typically involves moving a cell, attacking an opponent cell or selecting a cell
    to spawn a new one.
    """

    def __init__(self, match_actions_service: "MatchActionsService"):
        super().__init__(match_actions_service)
        self._logger = get_configured_logger(__name__)
        self._turn_state = self._match_actions_service.turn_state

    @ActionManager.entry_point(with_turn_state_reset=True)
    def handle_cell_selection(self, cell_row: int, cell_col: int):
        """
        Handles the cell selection from the current player.
        """
        player = self.get_current_player()
        is_player_1 = player.is_player_1
        cell: Cell = self._game_board.get(cell_row, cell_col)

        if cell.belongs_to_player(player):
            self._handle_own_cell_selection(cell, is_player_1)

        # the cell belongs to the opponent
        elif cell.is_owned():
            self._handle_opponent_cell_selection(cell, is_player_1)

        # the cell is idle
        else:
            self._handle_idle_cell_selection(cell, is_player_1)

    def _handle_own_cell_selection(self, cell: Cell, player1: bool):
        """
        Handles all possible cases resulting from a player selecting a cell of their own.

        For example, if the player mode is set to owned cell selection, than the possible actions are either
        move, attack, or no action.
        """
        player_mode = self.get_player_mode()

        if player_mode == PlayerMode.IDLE:
            self.set_selected_cell(cell)
            self.get_possible_movements_and_attacks(player1)

        elif player_mode == PlayerMode.OWN_CELL_SELECTED:
            if self.get_selected_cell() == cell:
                self.set_player_as_idle()

            elif cell.is_owned():
                self.set_error_message(ErrorMessages.CANNOT_MOVE_TO_NOR_ATTACK)

        elif player_mode == PlayerMode.CELL_SPAWN:
            self.set_error_message(ErrorMessages.SELECT_IDLE_CELL)

        elif player_mode == PlayerMode.SPELL_SELECTED:
            spell_action = SpellCasting.create(
                player1,
                self.get_selected_spell(),
                cell.row_index,
                cell.column_index,
            )

            self.validate_and_process_action(spell_action)

    def _handle_opponent_cell_selection(self, cell: Cell, player1: bool):
        """
        Handles all possible cases resulting from a player selecting an enemy cell of their own.

        For example, if the player mode is set to owned cell selection, than there
        shouldn't be any possible action.
        """
        player_mode = self.get_player_mode()
        if player_mode == PlayerMode.IDLE:
            return  # no action possible

        selected_cell = self.get_selected_cell()
        if player_mode == PlayerMode.OWN_CELL_SELECTED:
            attack = CellAttack.create(
                player1,
                selected_cell.id,
                selected_cell.get_coordinates(),
                cell.get_coordinates(),
            )
            # self.validate_and_process_action(attack)
            self.validate_and_process_action(
                attack, with_post_processing_recalculation=True
            )

        elif player_mode == PlayerMode.CELL_SPAWN:
            self.set_error_message(ErrorMessages.SELECT_IDLE_CELL)

        elif player_mode == PlayerMode.SPELL_SELECTED:
            current_player = self.get_current_player()
            selected_spell = self.get_selected_spell()

            spell_action = SpellCasting.create(
                current_player.is_player_1,
                selected_spell,
                cell.row_index,
                cell.column_index,
            )

            self.validate_and_process_action(spell_action)

    def _handle_idle_cell_selection(self, cell: Cell, player1: bool):
        """
        Handles all possible cases resulting from a player selecting an idle cell.

        For example, if the player mode is set to cell spawn, than there may be a spawn action.
        """
        player_mode = self.get_player_mode()
        if player_mode == PlayerMode.IDLE:
            return  # no action possible

        if player_mode == PlayerMode.OWN_CELL_SELECTED:
            selected_cell = self.get_selected_cell()
            movement = CellMovement.create(
                player1,
                selected_cell.id,
                selected_cell.row_index,
                selected_cell.column_index,
                cell.row_index,
                cell.column_index,
            )
            # self.validate_and_process_action(movement)
            self.validate_and_process_action(
                movement, with_post_processing_recalculation=True
            )

        elif player_mode == PlayerMode.CELL_SPAWN:
            spawn = CellSpawn.create(player1, cell.row_index, cell.column_index)
            self.validate_and_process_action(
                spawn, with_post_processing_recalculation=True
            )

        elif player_mode == PlayerMode.SPELL_SELECTED:
            current_player = self.get_current_player()
            selected_spell = self.get_selected_spell()

            spell_action = SpellCasting.create(
                current_player.is_player_1,
                selected_spell,
                cell.row_index,
                cell.column_index,
            )

            self.validate_and_process_action(spell_action)

    @ActionManager.initialize_transient_board(force_reset=False)
    def get_possible_movements_and_attacks(
        self, player1: bool, recalculating: bool = False
    ):
        """
        Returns the concatenated possible movements and attacks a cell may perform.

        Note : A freshly spawned cell cannot move or attack.
        """
        possible_movements_and_attacks = get_possible_movements_and_attacks(
            player1,
            self.get_selected_cell(),
            self.get_transient_game_board(),
            self._turn_state,
        )
        if possible_movements_and_attacks:
            self.set_possible_actions(
                possible_movements_and_attacks, update_server_mode=not recalculating
            )
        elif recalculating:
            self.set_server_mode(ServerMode.SHOW_PROCESSED_ACTION)
        else:
            self.set_player_as_idle()

    @ActionManager.initialize_transient_board(force_reset=False)
    def set_selected_cell(self, cell: Cell):
        transient_game_board = self.get_transient_game_board()

        self.set_player_mode(PlayerMode.OWN_CELL_SELECTED)
        # Do not call the method from TransientTurnStateHolder to avoid recursive calls
        self.transient_turn_state.selected_cell = cell

        corresponding_cell = transient_game_board.get(cell.row_index, cell.column_index)
        corresponding_cell.set_selected()
