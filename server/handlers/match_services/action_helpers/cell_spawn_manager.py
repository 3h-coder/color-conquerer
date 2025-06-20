from typing import TYPE_CHECKING

from game_engine.action_calculation import get_possible_spawns
from handlers.match_services.action_helpers.abstract.action_manager import ActionManager
from handlers.match_services.action_helpers.enums.player_mode import PlayerMode

if TYPE_CHECKING:
    from handlers.match_services.match_actions_service import MatchActionsService


class CellSpawnManager(ActionManager):
    """
    Helper class to handle cell spawns from the current player.
    """

    def __init__(self, match_actions_service: "MatchActionsService"):
        super().__init__(match_actions_service)

    @ActionManager.entry_point
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

    @ActionManager.initialize_transient_board(force_reset=True)
    def find_possible_spawns(self, recalculating=False):
        """
        Sets the player mode to CELL_SPAWN and fills the possible actions field with
        the potential spawns.
        """
        player = self.get_current_player()
        transient_game_board = self.get_transient_game_board()

        possible_spawns = get_possible_spawns(player.is_player_1, transient_game_board)

        self.set_player_mode(PlayerMode.CELL_SPAWN)
        self.set_possible_actions(possible_spawns, update_server_mode=not recalculating)
