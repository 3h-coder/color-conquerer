from game_engine.models.actions.action import Action
from game_engine.models.actions.hooks.action_hook import ActionHook
from game_engine.models.dtos.match_context import MatchContext


class StaminaRestorationHook(ActionHook):
    """
    Increases the player's stamina points by 1.
    """

    def trigger(self, action: Action, match_context: MatchContext):
        player_resources = match_context.get_player_resources(action.from_player1)
        player_resources.current_stamina = min(
            player_resources.max_stamina, player_resources.current_stamina + 1
        )
