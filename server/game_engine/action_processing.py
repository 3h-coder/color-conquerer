from config.logging import get_configured_logger
from game_engine.models.actions.abstract.action import Action
from game_engine.models.match.match_context import MatchContext
from game_engine.models.player.player_resources import PlayerResources

_logger = get_configured_logger(__name__)


def process_action(action: Action, match_context: MatchContext) -> Action:
    player_resources = match_context.get_player_resources(action.from_player1)

    _process_player_mana(player_resources, action)

    action.apply(match_context)

    return action


def _process_player_mana(player_resources: PlayerResources, action: Action):
    """
    Processes the player mana regeneration.
    """
    if action.mana_cost > player_resources.current_mp:
        _logger.critical(
            f"Tried to perform an action with not enough mana. Action -> ({action})"
        )
        raise ValueError(f"Tried to perform an action with not enough mana.")

    player_resources.current_mp -= action.mana_cost
