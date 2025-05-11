from typing import TYPE_CHECKING

from game_engine.models.actions.action import Action
from game_engine.models.actions.cell_attack import CellAttack
from game_engine.models.actions.cell_movement import CellMovement
from game_engine.models.cell.cell import Cell
from handlers.match_services.action_helpers.abstract.action_manager import ActionManager
from handlers.match_services.action_helpers.action_processor import ActionProcessor
from handlers.match_services.action_helpers.enums.error_messages import ErrorMessages
from handlers.match_services.action_helpers.enums.player_mode import PlayerMode
from handlers.match_services.action_helpers.enums.server_mode import ServerMode

if TYPE_CHECKING:
    from handlers.match_services.match_actions_service import MatchActionsService


class CommonActionManager(ActionManager):
    """
    Helper class that contains common logic for all action managers to invoke.
    """

    def __init__(self, match_actions_service: "MatchActionsService"):
        super().__init__(match_actions_service)

        self.match_context = self._match_actions_service.match_context
        self.turn_state = self._match_actions_service.turn_state

        # region Match persistent fields

        self._actions_per_turn = self._match_actions_service.actions_per_turn
        self._action_processor = ActionProcessor(self.match_context, logger=self.logger)

        # endregion

    def validate_and_process_action(
        self, action: Action, with_post_processing_recalculation: bool = False
    ):
        """
        Validates the given action and processes it if it is valid.
        """
        if action not in self.get_possible_actions():
            self._logger.error(
                f"The following action was not registered in the possible actions : {action}"
            )

            player_mode = self.get_player_mode()
            if player_mode == PlayerMode.SPELL_SELECTED:
                selected_spell = self.get_selected_spell()
                self.set_error_message(selected_spell.INVALID_SELECTION_ERROR_MESSAGE)
            else:
                self.set_error_message(ErrorMessages.INVALID_ACTION)
            return

        current_player = self._match_actions_service.current_player
        if action.mana_cost > current_player.resources.current_mp:
            self.set_error_message(ErrorMessages.NOT_ENOUGH_MANA)
            return

        self._process_action(action, with_post_processing_recalculation)

    def trigger_callbacks(self):
        """
        Triggers all of the processed action's callbacks (if any)
        """
        processed_action = self.get_processed_action()
        if processed_action is None or not processed_action.has_callbacks_to_trigger():
            return

        self._logger.debug(
            f"Triggering the callbacks for the action : {processed_action}"
        )
        triggered_callbacks = set()
        for callback in self._action_processor.trigger_callbacks(processed_action):
            self._recalculate_possible_actions()

            triggered_callbacks.add(callback)
            yield callback

        self.set_triggered_callbacks(triggered_callbacks)

    def _process_action(
        self,
        action: Action,
        with_post_processing_recalculation,
    ):
        """
        Processes all of the given actions, setting the associate fields along the way.

        Note : Action validation should be done before calling this method.
        """
        server_mode = (
            ServerMode.SHOW_PROCESSED_AND_POSSIBLE_ACTIONS
            if with_post_processing_recalculation
            else ServerMode.SHOW_PROCESSED_ACTION
        )
        self.set_server_mode(server_mode)

        processed_action = self._action_processor.process_action(action)
        if processed_action is None:
            self.set_player_as_idle()
            self.set_error_message(ErrorMessages.INVALID_ACTION)
            return

        self._register_processed_action(processed_action)
        self._recalculate_possible_actions()

    def _register_processed_action(self, action: Action):
        """
        Adds a processed action to the turn and match actions fields.
        """
        # Set all the transient fields
        self.set_processed_action(action)
        self.set_error_message("")
        self.set_transient_game_board(None)

        # Register the action for record purposes
        current_turn = self.match_context.current_turn
        if current_turn not in self._actions_per_turn:
            self._actions_per_turn[current_turn] = []

        self._actions_per_turn[current_turn].append(action)

        if isinstance(action, CellMovement):
            self.turn_state.register_movement(action.cell_id)

        elif isinstance(action, CellAttack):
            self.turn_state.register_attack(action.cell_id)

    def _recalculate_possible_actions(self):
        """
        Meant to be called right after action/callback processing, to recalculate the possible actions
        and display them to the player.

        For example, display all the possible spawns right after spawning a cell.
        """
        server_mode = self.get_server_mode()
        if server_mode != ServerMode.SHOW_PROCESSED_AND_POSSIBLE_ACTIONS:
            return

        player_mode = self.get_player_mode()
        if player_mode == PlayerMode.CELL_SPAWN:
            self._match_actions_service.cell_spawn_manager.find_possible_spawns(
                recalculating=True
            )

        elif player_mode == PlayerMode.OWN_CELL_SELECTED:
            processed_action = self.get_processed_action()

            cell_to_select: Cell | None = None
            if isinstance(processed_action, CellMovement):
                new_cell_coordinates = processed_action.metadata.impacted_coords
                cell_to_select = self._game_board.get(
                    new_cell_coordinates.row_index,
                    new_cell_coordinates.column_index,
                )
            elif isinstance(processed_action, CellAttack):
                selected_cell_coordinates = self.get_selected_cell().get_coordinates()
                cell_to_select = self._game_board.get(
                    selected_cell_coordinates.row_index,
                    selected_cell_coordinates.column_index,
                )

            if not cell_to_select.belongs_to(processed_action.from_player1):
                # self._logger.debug(
                #     "The cell no longer belongs to the player, cancelling action recalculation"
                # )
                self.set_server_mode(ServerMode.SHOW_PROCESSED_ACTION)
            else:
                cell_selection_manager = (
                    self._match_actions_service.cell_selection_manager
                )
                cell_selection_manager.set_selected_cell(cell_to_select)
                cell_selection_manager.get_possible_movements_and_attacks(
                    processed_action.from_player1, recalculating=True
                )
