import functools
from typing import TYPE_CHECKING
from config.logging import get_configured_logger
from dto.partial_match_action_dto import PartialMatchActionDto
from dto.possible_actions_dto import PossibleActionsDto
from dto.processed_action_dto import ProcessedActionDto
from dto.server_only.match_action_dto import ActionType, MatchActionDto
from dto.server_only.match_closure_dto import EndingReason
from dto.server_only.player_info_dto import PlayerInfoDto
from handlers.match_services.action_calculator import ActionCalculator
from handlers.match_services.action_helpers.cell_selection_manager import (
    CellSelectionManager,
)
from handlers.match_services.action_helpers.error_messages import ErrorMessages
from handlers.match_services.action_helpers.player_mode import PlayerMode
from handlers.match_services.action_helpers.server_mode import ServerMode
from handlers.match_services.action_helpers.transient_turn_state import (
    TransientTurnState,
)
from handlers.match_services.action_helpers.transient_turn_state_holder import (
    TransientTurnStateHolder,
)
from handlers.match_services.action_processor import ActionProcessor
from handlers.match_services.client_notifications import (
    notify_action_error,
    notify_possible_actions,
    notify_processed_action,
)
from handlers.match_services.service_base import ServiceBase
from utils.board_utils import to_client_board_dto

if TYPE_CHECKING:
    from handlers.match_services.match_handler_unit import MatchHandlerUnit


class MatchActionsService2(ServiceBase, TransientTurnStateHolder):
    """
    Helper class responsible for handling action requests from each players.
    The class handles both the action validation and action processing.
    """

    def __init__(self, match_handler_unit: "MatchHandlerUnit"):
        ServiceBase.__init__(self, match_handler_unit)
        TransientTurnStateHolder.__init__(self, TransientTurnState())
        self._logger = get_configured_logger(__name__)

        # region Match persistent fields

        self._board_array = self.match.match_info.boardArray
        self.action_calculator = ActionCalculator(self.match_info)
        self._action_processor = ActionProcessor(self.match_info)

        # Dictionary storing all of the actions that happened during a match.
        # Key : turn number | Value : list of actions
        self.actions_per_turn: dict[int, list] = {}

        # endregion

        # region Turn persistent fields
        # ⚠️ Any field below is meant to be reset in the reset_for_new_turn method ⚠️

        # used to track all the cells that moved during the turn
        self.turn_movements: set[str] = set()
        # used to track all the cells that attacked during the turn
        self.turn_attacks: set[str] = set()
        self.current_player: PlayerInfoDto | None = None

        self._cell_selection_manager = CellSelectionManager(self)

    def _entry_point(func):
        """
        Decorator method to mark a method as en entry point for the service.

        This implies certain processing before and after the decorated method call
        such as checking for the game ending for example.
        """

        @functools.wraps(func)
        def wrapper(self: "MatchActionsService2", *args, **kwargs):
            self.current_player = self.match.get_current_player()
            func(self, *args, **kwargs)
            self._end_match_if_game_over()

        return wrapper

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

    def send_response_to_client(self):
        """
        Crucial method.

        Let's the client know the server's response to the player's request allowing it to render
        subsequent animations properly.
        """
        if error_msg := self.get_error_message():
            self._logger.debug(f"Sending to the client the error message : {error_msg}")
            notify_action_error(error_msg)
            return

        player_mode = self.get_player_mode()
        server_mode = self.get_server_mode()
        processed_action = self.get_processed_action()

        if server_mode == ServerMode.SHOW_POSSIBLE_ACTIONS:
            notify_possible_actions(
                PossibleActionsDto(
                    player_mode,
                    self._get_client_friendly_transient_board(),
                )
            )
            return

        processed_action_dto = ProcessedActionDto(
            PartialMatchActionDto.from_match_action_dto(processed_action),
            player_mode,
            self.match.get_turn_info(),
            None,
        )
        if server_mode == ServerMode.SHOW_PROCESSED_ACTION:
            notify_processed_action(
                processed_action_dto,
                self.room_id,
            )

        elif server_mode == ServerMode.SHOW_PROCESSED_AND_POSSIBLE_ACTIONS:
            processed_action_dto.overridingTransientBoard = (
                self._get_client_friendly_transient_board()
            )

            notify_processed_action(
                processed_action_dto,
                self.room_id,
            )

    @_entry_point
    def handle_cell_selection(self, cell_row: int, cell_col: int):
        self._cell_selection_manager.handle_cell_selection(cell_row, cell_col)

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

        if action.manaCost > self.current_player.playerGameInfo.currentMP:
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
        current_turn = self.match_info.currentTurn
        if current_turn not in self.actions_per_turn:
            self.actions_per_turn[current_turn] = []

        self.actions_per_turn[current_turn].append(action)

        cell_id = action.cellId
        if action.type == ActionType.CELL_MOVE:
            self.turn_movements.add(cell_id)

        elif action.type == ActionType.CELL_ATTACK:
            self.turn_attacks.add(cell_id)

    def _calculate_post_processing_possible_actions(self):
        """
        Meant to be called right after action processing.
        """
        self.set_transient_board_array(None)
        server_mode = self.get_server_mode()
        player_mode = self.get_player_mode()

        if server_mode != ServerMode.SHOW_PROCESSED_AND_POSSIBLE_ACTIONS:
            return

        if player_mode == PlayerMode.CELL_SPAWN:
            # self._cell_spawn_manager.find_possible_spawns()
            pass

    def _get_client_friendly_transient_board(self):
        transient_board_array = self.get_transient_board_array()
        return (
            to_client_board_dto(transient_board_array)
            if transient_board_array
            else to_client_board_dto(self._board_array)
        )
