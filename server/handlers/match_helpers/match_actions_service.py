import functools
from enum import IntEnum, StrEnum
from typing import TYPE_CHECKING

from config.logging import get_configured_logger
from constants.match_constants import BOARD_SIZE
from dto.partial_match_action_dto import PartialMatchActionDto
from dto.partial_match_info_dto import PartialMatchInfoDto
from dto.possible_actions_dto import PossibleActionsDto
from dto.processed_action_dto import ProcessedActionDto
from dto.server_only.cell_info_dto import CellInfoDto
from dto.server_only.match_action_dto import ActionType, MatchActionDto
from dto.server_only.match_closure_dto import EndingReason
from dto.server_only.player_info_dto import PlayerInfoDto
from game_engine.spells.spell_base import SpellBase
from game_engine.spells.spell_factory import get_spell
from handlers.match_helpers.action_calculator import ActionCalculator
from handlers.match_helpers.action_processor import ActionProcessor
from handlers.match_helpers.client_notifications import (
    notify_action_error,
    notify_possible_actions,
    notify_processed_action,
)
from handlers.match_helpers.service_base import ServiceBase
from utils.board_utils import copy_board, to_client_board_dto

if TYPE_CHECKING:
    from handlers.match_helpers.match_handler_unit import MatchHandlerUnit


class PlayerMode(IntEnum):
    # Default, the player is expected to select a cell, spawn a cell, or select a spell
    IDLE = 0
    # The player just selected a cell of their own and is expected to perform an action from it (move or attack)
    OWN_CELL_SELECTED = 1
    # A spawn action is being awaited on an idle cell with no owner
    CELL_SPAWN = 2
    # The player selected a spell, an action is possible on any cell as this depends on the spell
    SPELL_SELECTED = 3


class ServerMode(IntEnum):
    # The server intends to show the possible actions to the player whose turn it is
    SHOW_POSSIBLE_ACTIONS = 0
    # The server intends to show the processed action to both players
    SHOW_PROCESSED_ACTION = 1
    # The server intends to show the processed action and the resulting possible actions from it simultaneously
    # (example: all possible spawns after spawning a new cell)
    SHOW_PROCESSED_AND_POSSIBLE_ACTIONS = 2


class ErrorMessages(StrEnum):
    CANNOT_MOVE_TO_NOR_ATTACK = "Cannot move to nor attack this cell"
    SELECT_IDLE_CELL = "You must select an idle cell"
    NOT_ENOUGH_MANA = "Not enough mana"
    INVALID_ACTION = "Invalid action"  # The client should prevent this message from being shown, but just in case


class MatchActionsService(ServiceBase):
    """
    Helper class responsible for handling action requests from each players.
    The class handles both the action validation and action processing.
    """

    def __init__(self, match_handler_unit: "MatchHandlerUnit"):
        super().__init__(match_handler_unit)
        self._logger = get_configured_logger(__name__)

        # region Match persistent fields

        self._board_array = self.match.match_info.boardArray
        self._action_calculator = ActionCalculator(self.match_info)
        self._action_processor = ActionProcessor(self.match_info)

        # Dictionary storing all of the actions that happened during a match.
        # Key : turn number | Value : list of actions
        self.actions_per_turn: dict[int, list] = {}

        # endregion

        # region Turn persistent fields
        # ⚠️ Any field below is meant to be reset in the reset_for_new_turn method ⚠️

        # used to track all the cells that moved during the turn
        self._turn_movements: set[str] = set()
        # used to track all the cells that attacked during the turn
        self._turn_attacks: set[str] = set()
        self._current_player: PlayerInfoDto = None

        # endregion

        # region Player action state fields
        # ⚠️ Any field below is meant to be reset in the _set_player_to_idle method ⚠️

        # Used to confirm whether an action can be done or not
        self._possible_actions: set[MatchActionDto] = set()
        # Actions that have been validated and applied,
        # overridden each time a set of action is processed
        self._processed_action: MatchActionDto = None
        self._player_mode = PlayerMode.IDLE
        self._server_mode = ServerMode.SHOW_POSSIBLE_ACTIONS
        # Board copy to save and send to the client the transient states
        # resulting from the possible actions.
        self._transient_board_array: list[list[CellInfoDto]] = None
        # Applicable when the player mode is OWN_CELL_SELECTED
        self._selected_cell: CellInfoDto = None
        # Applicable when the player mode is SPELL_SELECTED
        self._selected_spell: SpellBase = None
        # Message to the player when their request is invalid
        self._error_msg: str = ""

        # endregion

    def _initialize_transient_board(func):
        """
        Decorator method that ensures the transient board is properly initialized.

        To be wrapped around any method that uses the transient board.
        """

        @functools.wraps(func)
        def wrapper(self: "MatchActionsService", *args, **kwargs):
            if self._transient_board_array is None:
                self._transient_board_array = copy_board(self._board_array)
            return func(self, *args, **kwargs)

        return wrapper

    def _entry_point(func):
        """
        Decorator method to mark a mathod as en entry point for the service.

        This implies certain processing afterwards such as checking for the game ending for example.
        """

        @functools.wraps(func)
        def wrapper(self: "MatchActionsService", *args, **kwargs):
            self._current_player = self.match.get_current_player()
            func(self, *args, **kwargs)
            self._end_match_if_game_over()

        return wrapper

    def reset_for_new_turn(self):
        """
        Performs all the cleanup and reset necessary for a fresh new turn.

        Meant to be used as a callback for the turn watcher service.
        """
        self.actions_per_turn[self.match_info.currentTurn] = []
        self._turn_movements = set()
        self._turn_attacks = set()
        self._current_player = self.match.get_current_player()
        self.set_player_as_idle()

    def set_player_as_idle(self):
        """
        Resets all the temporary fields used to store the state of the current player's action.

        This is an effective reset of a player's action state.

        Note : This will also reset any error message.
        """
        self._player_mode = PlayerMode.IDLE
        self._server_mode = ServerMode.SHOW_POSSIBLE_ACTIONS
        self._possible_actions = set()
        self._processed_action = None
        self._transient_board_array = None
        self._selected_cell = None
        self._selected_spell = None
        self._error_msg = ""

    @_entry_point
    def handle_cell_selection(self, cell_row: int, cell_col: int):
        """
        Handles the selection of a cell. This can either trigger an action or return a list of possible actions.
        """
        player = self._current_player
        is_player_1 = player.isPlayer1
        cell: CellInfoDto = self._board_array[cell_row][cell_col]

        if cell.belongs_to(player):
            self._handle_own_cell_selection(cell, is_player_1)

        # the cell belongs to the opponent
        elif cell.is_owned():
            self._handle_opponent_cell_selection(cell, is_player_1)

        # the cell is idle
        else:
            self._handle_idle_cell_selection(cell, is_player_1)

        self._send_response()

        if self._server_mode == ServerMode.SHOW_PROCESSED_ACTION:
            self.set_player_as_idle()

    @_entry_point
    def handle_spawn_toggle(self):
        """
        Handles the spawn/spawn cancellation request of a player.
        """
        if self._player_mode == PlayerMode.IDLE:
            self._find_possible_spawns()

        elif self._player_mode == PlayerMode.OWN_CELL_SELECTED:
            self.set_player_as_idle()
            self._find_possible_spawns()

        elif self._player_mode == PlayerMode.CELL_SPAWN:
            self.set_player_as_idle()

        elif self._player_mode == PlayerMode.SPELL_SELECTED:
            self.set_player_as_idle()
            self._find_possible_spawns()

        self._send_response()

    @_entry_point
    def handle_spell_request(self, spell_id: int):
        """
        Handles the spell request of a player.
        """
        if self._player_mode == PlayerMode.IDLE:
            self._find_spell_possible_targets(spell_id)

        else:
            self.set_player_as_idle()
            self._find_spell_possible_targets(spell_id)

        self._send_response()

    def _handle_own_cell_selection(self, cell: CellInfoDto, player1: bool):
        """
        Handles all possible cases resulting from a player selecting a cell of their own.

        For example, if the player mode is set to owned cell selection, than the possible actions are either
        move, attack, or no action.
        """
        if self._player_mode == PlayerMode.IDLE:
            self._set_selected_cell(cell)
            possible_actions = self._get_possible_movements_and_attacks(player1)
            if possible_actions:
                self._set_possible_actions(set(possible_actions))
            else:
                self.set_player_as_idle()

        elif self._player_mode == PlayerMode.OWN_CELL_SELECTED:

            if self._selected_cell == cell:
                self.set_player_as_idle()

            elif cell.is_owned():
                self._error_msg = ErrorMessages.CANNOT_MOVE_TO_NOR_ATTACK

        elif self._player_mode == PlayerMode.CELL_SPAWN:
            self._error_msg = ErrorMessages.SELECT_IDLE_CELL

        elif self._player_mode == PlayerMode.SPELL_SELECTED:
            spell_action = MatchActionDto.spell(
                self._current_player.isPlayer1,
                self._selected_spell,
                cell.rowIndex,
                cell.columnIndex,
            )

            self._validate_and_process_action(spell_action)

    def _handle_opponent_cell_selection(self, cell: CellInfoDto, player1: bool):
        """
        Handles all possible cases resulting from a player selecting an enemy cell of their own.

        For example, if the player mode is set to owned cell selection, than there
        shouldn't be any possible action.
        """
        if self._player_mode == PlayerMode.IDLE:
            pass  # no action possible

        elif self._player_mode == PlayerMode.OWN_CELL_SELECTED:
            attack = MatchActionDto.cell_attack(
                player1,
                self._selected_cell.id,
                self._selected_cell.rowIndex,
                self._selected_cell.columnIndex,
                cell.rowIndex,
                cell.columnIndex,
            )
            self._validate_and_process_action(attack)

        elif self._player_mode == PlayerMode.CELL_SPAWN:
            self._error_msg = ErrorMessages.SELECT_IDLE_CELL

        elif self._player_mode == PlayerMode.SPELL_SELECTED:
            spell_action = MatchActionDto.spell(
                self._current_player.isPlayer1,
                self._selected_spell,
                cell.rowIndex,
                cell.columnIndex,
            )

            self._validate_and_process_action(spell_action)

    def _handle_idle_cell_selection(self, cell: CellInfoDto, player1: bool):
        """
        Handles all possible cases resulting from a player selecting an idle cell.

        For example, if the player mode is set to cell spawn, than there may be a spawn action.
        """
        if self._player_mode == PlayerMode.IDLE:
            pass  # no action possible

        elif self._player_mode == PlayerMode.OWN_CELL_SELECTED:
            movement = MatchActionDto.cell_movement(
                player1,
                self._selected_cell.id,
                self._selected_cell.rowIndex,
                self._selected_cell.columnIndex,
                cell.rowIndex,
                cell.columnIndex,
            )
            self._validate_and_process_action(movement)

        elif self._player_mode == PlayerMode.CELL_SPAWN:
            spawn = MatchActionDto.cell_spawn(player1, cell.rowIndex, cell.columnIndex)
            self._validate_and_process_action(
                spawn, server_mode=ServerMode.SHOW_PROCESSED_AND_POSSIBLE_ACTIONS
            )

        elif self._player_mode == PlayerMode.SPELL_SELECTED:
            spell_action = MatchActionDto.spell(
                self._current_player.isPlayer1,
                self._selected_spell,
                cell.rowIndex,
                cell.columnIndex,
            )

            self._validate_and_process_action(spell_action)

    def _send_response(self):
        """
        Crucial method.

        Let's the client know the server's response to the player's request allowing it to render
        subsequent animations properly.
        """
        if self._error_msg:
            self._logger.debug(
                f"Sending to the client the error message : {self._error_msg}"
            )
            notify_action_error(self._error_msg)
            return

        if self._server_mode == ServerMode.SHOW_POSSIBLE_ACTIONS:
            notify_possible_actions(
                PossibleActionsDto(
                    self._player_mode,
                    self._get_client_friendly_transient_board(),
                )
            )
            return

        processed_action_dto = ProcessedActionDto(
            PartialMatchActionDto.from_match_action_dto(self._processed_action),
            self._player_mode,
            self.match.get_turn_info(),
            None,
        )
        if self._server_mode == ServerMode.SHOW_PROCESSED_ACTION:
            notify_processed_action(
                processed_action_dto,
                self.room_id,
            )

        elif self._server_mode == ServerMode.SHOW_PROCESSED_AND_POSSIBLE_ACTIONS:
            processed_action_dto.overridingTransientBoard = (
                self._get_client_friendly_transient_board()
            )

            notify_processed_action(
                processed_action_dto,
                self.room_id,
            )

    def _set_possible_actions(
        self, actions: set[MatchActionDto], update_server_mode=True
    ):
        """
        Stores all of the possible actions and sets the server mode accordingly.
        """
        if update_server_mode:
            self._server_mode = ServerMode.SHOW_POSSIBLE_ACTIONS
        self._possible_actions = actions

    def _validate_and_process_action(
        self, action: MatchActionDto, server_mode=ServerMode.SHOW_PROCESSED_ACTION
    ):
        """
        Validates the given action and processes it if it is valid.
        """
        if action not in self._possible_actions:
            self._logger.error(
                f"The following action was not registered in the possible actions : {action}"
            )
            self._error_msg = ErrorMessages.INVALID_ACTION
            return

        if action.manaCost > self._current_player.playerGameInfo.currentMP:
            self._error_msg = ErrorMessages.NOT_ENOUGH_MANA
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
        self._server_mode = (
            server_mode
            if server_mode != ServerMode.SHOW_POSSIBLE_ACTIONS
            else ServerMode.SHOW_PROCESSED_ACTION
        )
        processed_action = self._action_processor.process_action(action)
        if processed_action is None:
            self.set_player_as_idle()
            self._error_msg = ErrorMessages.INVALID_ACTION
            return

        # Reset the error message as it is no longer relevant
        self._error_msg = ""

        self._processed_action = processed_action
        self._register_processed_action(processed_action)
        self._calculate_post_processing_possible_actions()

    def _register_processed_action(self, action: MatchActionDto):
        """
        Adds a processed action to the turn and match actions fields.
        """
        current_turn = self.match_info.currentTurn
        if current_turn not in self.actions_per_turn:
            self.actions_per_turn[current_turn] = []

        self.actions_per_turn[current_turn].append(action)

        cell_id = action.cellId
        if action.type == ActionType.CELL_MOVE:
            self._turn_movements.add(cell_id)

        elif action.type == ActionType.CELL_ATTACK:
            self._turn_attacks.add(cell_id)

    def _calculate_post_processing_possible_actions(self):
        """
        Meant to be called right after action processing.
        """
        self._transient_board_array = None

        if self._server_mode != ServerMode.SHOW_PROCESSED_AND_POSSIBLE_ACTIONS:
            return

        if self._player_mode == PlayerMode.CELL_SPAWN:
            self._find_possible_spawns(update_server_mode=False)

    def _end_match_if_game_over(self):
        """
        Ends the match if at least one player dies.
        """
        player1 = self.match_info.player1
        player2 = self.match_info.player2

        if self.match_info.both_players_are_dead():
            self.match.end(EndingReason.DRAW)

        elif self.match_info.player1_is_dead():
            self.match.end(EndingReason.PLAYER_WON, loser_id=player1.playerId)

        elif self.match_info.player2_is_dead():
            self.match.end(EndingReason.PLAYER_WON, loser_id=player2.playerId)

    @_initialize_transient_board
    def _set_selected_cell(self, cell: CellInfoDto):
        """
        Sets the player mode and selected cell fields accordingly.
        """
        self._player_mode = PlayerMode.OWN_CELL_SELECTED
        self._selected_cell = cell
        transient_cell = self._transient_board_array[cell.rowIndex][cell.columnIndex]
        transient_cell.set_selected()

    @_initialize_transient_board
    def _get_possible_movements_and_attacks(self, player1: bool):
        """
        Returns the concatenated possible movements and attacks a cell may perform.

        Note : A freshly spawned cell cannot move or attack.
        """
        if self._selected_cell.is_freshly_spawned():
            return []

        movements: list[MatchActionDto] = []
        attacks: list[MatchActionDto] = []

        if not self._selected_cell_has_already_moved_this_turn():
            movements = self._action_calculator.calculate_possible_movements(
                self._selected_cell, player1, self._transient_board_array
            )

        if not self._selected_cell_has_already_attacked_this_turn():
            attacks = self._action_calculator.calculate_possible_attacks(
                self._selected_cell, player1, self._transient_board_array
            )

        return movements + attacks

    @_initialize_transient_board
    def _find_possible_spawns(self, update_server_mode=True):
        """
        Sets the player mode to CELL_SPAWN and fills the possible actions field with
        the potential spawns.
        """
        player = self._current_player
        possible_spawns = self._action_calculator.calculate_possible_spawns(
            player.isPlayer1, self._transient_board_array
        )
        self._player_mode = PlayerMode.CELL_SPAWN
        self._set_possible_actions(possible_spawns, update_server_mode)

    @_initialize_transient_board
    def _find_spell_possible_targets(self, spell_id: int):
        """
        Sets the player mode to SPELL_SELECTED and fills the possible actions field with
        the potential targets of the spell.
        """
        player = self._current_player
        spell = get_spell(spell_id)
        possible_spell_invocations = (
            self._action_calculator.calculate_possible_spell_targets(
                spell, player.isPlayer1, self._transient_board_array
            )
        )
        self._player_mode = PlayerMode.SPELL_SELECTED
        self._selected_spell = spell
        self._set_possible_actions(possible_spell_invocations)

    def _selected_cell_has_already_moved_this_turn(self):
        return (
            self._selected_cell is not None
            and self._selected_cell.id in self._turn_movements
        )

    def _selected_cell_has_already_attacked_this_turn(self):
        return (
            self._selected_cell is not None
            and self._selected_cell.id in self._turn_attacks
        )

    def _get_client_friendly_transient_board(self):
        return (
            to_client_board_dto(self._transient_board_array)
            if self._transient_board_array
            else to_client_board_dto(self._board_array)
        )
