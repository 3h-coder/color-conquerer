from typing import TYPE_CHECKING

from config.logging import get_configured_logger
from dto.server_only.match_action_dto import MatchActionDto
from game_engine.models.cell.cell import Cell
from handlers.match_services.action_helpers.action_manager import ActionManager
from handlers.match_services.action_helpers.error_messages import ErrorMessages
from handlers.match_services.action_helpers.player_mode import PlayerMode
from handlers.match_services.action_helpers.server_mode import ServerMode

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

    def handle_cell_selection(self, cell_row: int, cell_col: int):
        """
        Handles the cell selection from the current player.
        """
        player = self.get_current_player()
        is_player_1 = player.is_player_1
        cell: Cell = self._board_array[cell_row][cell_col]

        if cell.belongs_to(player):
            self._handle_own_cell_selection(cell, is_player_1)

        # the cell belongs to the opponent
        elif cell.is_owned():
            self._handle_opponent_cell_selection(cell, is_player_1)

        # the cell is idle
        else:
            self._handle_idle_cell_selection(cell, is_player_1)

        self.send_response_to_client()

        if self.get_server_mode() == ServerMode.SHOW_PROCESSED_ACTION:
            self.set_player_as_idle()

    def _handle_own_cell_selection(self, cell: Cell, player1: bool):
        """
        Handles all possible cases resulting from a player selecting a cell of their own.

        For example, if the player mode is set to owned cell selection, than the possible actions are either
        move, attack, or no action.
        """
        player_mode = self.get_player_mode()

        if player_mode == PlayerMode.IDLE:
            self._set_selected_cell(cell)
            possible_actions = self._get_possible_movements_and_attacks(player1)
            if possible_actions:
                self.set_possible_actions(set(possible_actions))
            else:
                self.set_player_as_idle()

        elif player_mode == PlayerMode.OWN_CELL_SELECTED:
            if self.get_selected_cell() == cell:
                self.set_player_as_idle()

            elif cell.is_owned():
                self.set_error_message(ErrorMessages.CANNOT_MOVE_TO_NOR_ATTACK)

        elif player_mode == PlayerMode.CELL_SPAWN:
            self.set_error_message(ErrorMessages.SELECT_IDLE_CELL)

        elif player_mode == PlayerMode.SPELL_SELECTED:
            spell_action = MatchActionDto.spell(
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
            attack = MatchActionDto.cell_attack(
                player1,
                selected_cell.id,
                selected_cell.row_index,
                selected_cell.column_index,
                cell.row_index,
                cell.column_index,
            )
            self.validate_and_process_action(attack)

        elif player_mode == PlayerMode.CELL_SPAWN:
            self.set_error_message(ErrorMessages.SELECT_IDLE_CELL)

        elif player_mode == PlayerMode.SPELL_SELECTED:
            current_player = self.get_current_player()
            selected_spell = self.get_selected_spell()

            spell_action = MatchActionDto.spell(
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
            movement = MatchActionDto.cell_movement(
                player1,
                selected_cell.id,
                selected_cell.row_index,
                selected_cell.column_index,
                cell.row_index,
                cell.column_index,
            )
            self.validate_and_process_action(movement)

        elif player_mode == PlayerMode.CELL_SPAWN:
            spawn = MatchActionDto.cell_spawn(
                player1, cell.row_index, cell.column_index
            )
            self.validate_and_process_action(
                spawn, server_mode=ServerMode.SHOW_PROCESSED_AND_POSSIBLE_ACTIONS
            )

        elif player_mode == PlayerMode.SPELL_SELECTED:
            current_player = self.get_current_player()
            selected_spell = self.get_selected_spell()

            spell_action = MatchActionDto.spell(
                current_player.is_player_1,
                selected_spell,
                cell.row_index,
                cell.column_index,
            )

            self.validate_and_process_action(spell_action)

    @ActionManager.initialize_transient_board
    def _get_possible_movements_and_attacks(self, player1: bool):
        """
        Returns the concatenated possible movements and attacks a cell may perform.

        Note : A freshly spawned cell cannot move or attack.
        """
        selected_cell = self.get_selected_cell()
        if selected_cell.is_freshly_spawned():
            return []

        action_calculator = self._match_actions_service.action_calculator
        transient_board = self.get_transient_board_array()
        movements: list[MatchActionDto] = []
        attacks: list[MatchActionDto] = []

        if not self._has_already_moved_this_turn(selected_cell):
            movements = action_calculator.calculate_possible_movements(
                selected_cell, player1, transient_board
            )

        if not self._has_already_attacked_this_turn(selected_cell):
            attacks = action_calculator.calculate_possible_attacks(
                selected_cell, player1, transient_board
            )

        return movements + attacks

    @ActionManager.initialize_transient_board
    def _set_selected_cell(self, cell: Cell):
        transient_board_array = self.get_transient_board_array()

        self.set_player_mode(PlayerMode.OWN_CELL_SELECTED)
        self.set_selected_cell(cell)

        corresponding_cell: Cell = transient_board_array[cell.row_index][
            cell.column_index
        ]
        corresponding_cell.set_selected()

    def _has_already_moved_this_turn(self, cell: Cell):
        return (
            cell is not None
            and cell.id in self._match_actions_service.turn_state.movements
        )

    def _has_already_attacked_this_turn(self, cell: Cell):
        return (
            cell is not None
            and cell.id in self._match_actions_service.turn_state.attacks
        )
