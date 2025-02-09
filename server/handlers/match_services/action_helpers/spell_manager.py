from typing import TYPE_CHECKING

from config.logging import get_configured_logger
from game_engine.action_calculation import get_possible_spell_castings
from game_engine.models.spells.spell_factory import get_spell
from handlers.match_services.action_helpers.action_manager import ActionManager
from handlers.match_services.action_helpers.player_mode import PlayerMode

if TYPE_CHECKING:
    from handlers.match_services.match_actions_service import MatchActionsService


class SpellManager(ActionManager):
    """
    Helper class to handle spell selections from the current player.
    """

    def __init__(self, match_actions_service: "MatchActionsService"):
        super().__init__(match_actions_service)
        self._logger = get_configured_logger(__name__)

    def handle_spell_request(self, spell_id: int):
        player_mode = self.get_player_mode()
        selected_spell = self.get_selected_spell()

        if player_mode == PlayerMode.IDLE:
            self._find_spell_possible_targets(spell_id)

        elif player_mode == PlayerMode.SPELL_SELECTED:
            if spell_id == selected_spell.id:
                self.set_player_as_idle()
            else:
                self._find_spell_possible_targets(spell_id)

        else:
            self.set_player_as_idle()
            self._find_spell_possible_targets(spell_id)

        self.send_response_to_client()

    @ActionManager.initialize_transient_board
    def _find_spell_possible_targets(self, spell_id: int):
        """
        Sets the player mode to SPELL_SELECTED and fills the possible actions field with
        the potential targets of the spell.
        """
        player = self.get_current_player()
        transient_board_array = self.get_transient_board_array()
        spell = get_spell(spell_id)

        possible_spell_invocations = get_possible_spell_castings(
            spell, player.is_player_1, transient_board_array
        )

        self.set_player_mode(PlayerMode.SPELL_SELECTED)
        self.set_selected_spell(spell)
        self.set_possible_actions(possible_spell_invocations)
