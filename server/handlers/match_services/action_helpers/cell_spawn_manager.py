from typing import TYPE_CHECKING

from config.logging import get_configured_logger
from handlers.match_services.action_helpers.action_manager import ActionManager
from handlers.match_services.action_helpers.player_mode import PlayerMode

if TYPE_CHECKING:
    from handlers.match_services.match_actions_service import MatchActionsService


class CellSpawnManager(ActionManager):
    """
    Helper class to handle cell spawns from the current player.
    """

    def __init__(self, match_actions_service: "MatchActionsService"):
        super().__init__(match_actions_service)
        self._logger = get_configured_logger(__name__)

    def handle_spawn_toggle(self):
        """
        Handles the spawn/spawn cancellation request of a player.
        """
        player_mode = self.get_player_mode()
        if player_mode == PlayerMode.IDLE:
            self.find_possible_spawns()

        elif player_mode == PlayerMode.OWN_CELL_SELECTED:
            self.set_player_as_idle()
            self.find_possible_spawns()

        elif player_mode == PlayerMode.CELL_SPAWN:
            self.set_player_as_idle()

        elif player_mode == PlayerMode.SPELL_SELECTED:
            self.set_player_as_idle()
            self.find_possible_spawns()

        self.send_response_to_client()

    @ActionManager.initialize_transient_board
    def find_possible_spawns(self, update_server_mode=True):
        """
        Sets the player mode to CELL_SPAWN and fills the possible actions field with
        the potential spawns.
        """
        player = self.get_current_player()
        transient_board_array = self.get_transient_board_array()
        action_calculator = self._match_actions_service.action_calculator

        possible_spawns = action_calculator.calculate_possible_spawns(
            player.isPlayer1, transient_board_array
        )
        self.set_player_mode(PlayerMode.CELL_SPAWN)
        self.set_possible_actions(possible_spawns, update_server_mode)
