from config.logging import get_configured_logger
from game_engine.action_processing import process_action
from game_engine.models.actions.action import Action
from game_engine.models.match_context import MatchContext


class ActionProcessor:
    """
    Class responsible for the raw action processing and match info updating from it.

    Note : Action validation should be done before calling this class's methods.
    """

    def __init__(self, match_info: MatchContext):
        self._logger = get_configured_logger(__name__)
        self._match_context = match_info

    def process_action(self, action: Action):
        """
        Processes and applies the given action to the match info reference.

        This method should never fail, but is wrapped inside of a try except just in case.

        Returns True if the action could be processed properly, false otherwise.
        """
        try:
            return process_action(action, self._match_context)
        except Exception:
            self._logger.critical(
                f"Failed to process the action : {action}", exc_info=True
            )
            return None
