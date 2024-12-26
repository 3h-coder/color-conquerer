from config.logging import get_configured_logger
from dto.server_only.match_action_dto import ActionType, MatchActionDto
from dto.server_only.match_info_dto import MatchInfoDto
from utils.board_utils import move_cell, spawn_cell


class ActionProcessor:
    """
    Class responsible for the raw action processing and match info updating from it.

    Note : Action validation should be done before calling this class's methods.
    """

    def __init__(self, match_info: MatchInfoDto):
        self._logger = get_configured_logger(__name__)
        self._match_info = match_info
        self._board_array = match_info.boardArray

    def process_actions_sequentially(self, actions: set[MatchActionDto]):
        """
        Processes and applies the given action in the order they were given.

        Returns the set of actions that were processed properly.
        """
        processed_actions: set[MatchActionDto] = set()
        for action in actions:
            if self.process_action(action):
                processed_actions.add(action)

        return processed_actions

    def process_action(self, action: MatchActionDto):
        """
        Processes and applies the given action to the match info reference.

        This method should never fail, but is wrapped inside of a try except just in case.

        Returns True if the action could be processed properly, false otherwise.
        """
        action_type = action.type
        player_game_info = self._match_info.get_player_game_info(action.player1)
        try:
            if action.manaCost > player_game_info.currentMP:
                raise ValueError(
                    f"Player {action.player1} tried to perform an action with not enough mana."
                )

            if action_type == ActionType.CELL_MOVE:
                original_coords = action.originatingCellCoords
                new_coords = action.impactedCoords[0]
                move_cell(
                    original_coords.rowIndex,
                    original_coords.columnIndex,
                    new_coords.rowIndex,
                    new_coords.columnIndex,
                    self._board_array,
                )

            elif action_type == ActionType.CELL_ATTACK:
                pass  # nothing for now

            elif action_type == ActionType.CELL_SPAWN:
                coords = action.impactedCoords[0]
                spawn_cell(
                    coords.rowIndex,
                    coords.columnIndex,
                    action.player1,
                    self._board_array,
                )

            elif action_type == ActionType.PLAYER_SPELL:
                pass  # nothing for now

            return True
        except Exception:
            self._logger.critical(
                f"Failed to process the action : {action}", exc_info=True
            )
            return False
