from config.logging import get_configured_logger
from dto.player_game_info_dto import PlayerGameInfoDto
from dto.server_only.match_action_dto import ActionType, MatchActionDto
from dto.server_only.match_info_dto import MatchInfoDto
from utils.board_utils import move_cell, spawn_cell, trigger_cell_attack


class ActionProcessor:
    """
    Class responsible for the raw action processing and match info updating from it.

    Note : Action validation should be done before calling this class's methods.
    """

    def __init__(self, match_info: MatchInfoDto):
        self._logger = get_configured_logger(__name__)
        self._match_info = match_info
        self._board_array = match_info.boardArray

    def process_action(self, action: MatchActionDto):
        """
        Processes and applies the given action to the match info reference.

        This method should never fail, but is wrapped inside of a try except just in case.

        Returns True if the action could be processed properly, false otherwise.
        """
        action_type = action.type
        player_game_info = self._match_info.get_player_game_info(action.player1)
        try:
            self._process_player_mana(player_game_info, action)

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
                attacking_coords = action.originatingCellCoords
                target_coords = action.impactedCoords[0]
                trigger_cell_attack(
                    attacking_coords.rowIndex,
                    attacking_coords.columnIndex,
                    target_coords.rowIndex,
                    target_coords.columnIndex,
                    self._match_info,
                )

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

            return action
        except Exception:
            self._logger.critical(
                f"Failed to process the action : {action}", exc_info=True
            )
            return None

    def _process_player_mana(
        self, player_game_info: PlayerGameInfoDto, action: MatchActionDto
    ):
        """
        Processes the player mana regeneration.
        """
        if action.manaCost > player_game_info.currentMP:
            raise ValueError(
                f"Player {action.player1} tried to perform an action with not enough mana."
            )

        player_game_info.currentMP -= action.manaCost
