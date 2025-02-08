from config.logging import get_configured_logger
from dto.player_resources_dto import PlayerResourcesDto
from dto.server_only.match_action_dto import ActionType, MatchActionDto
from dto.server_only.match_context_dto import MatchContextDto
from game_engine.cell_actions import move_cell, spawn_cell, trigger_cell_attack
from game_engine.models.cell.cell import Cell
from game_engine.models.match_context import MatchContext
from game_engine.models.player_resources import PlayerResources
from game_engine.models.spells.spell_factory import get_spell


class ActionProcessor:
    """
    Class responsible for the raw action processing and match info updating from it.

    Note : Action validation should be done before calling this class's methods.
    """

    def __init__(self, match_info: MatchContext):
        self._logger = get_configured_logger(__name__)
        self._match_context = match_info
        self._board_array = match_info.board_array

    def process_action(self, action: MatchActionDto):
        """
        Processes and applies the given action to the match info reference.

        This method should never fail, but is wrapped inside of a try except just in case.

        Returns True if the action could be processed properly, false otherwise.
        """
        action_type = action.type
        player_game_info = self._match_context.get_player_resources(action.player1)
        try:
            self._process_player_mana(player_game_info, action)

            if action_type == ActionType.CELL_MOVE:
                original_coords = action.originatingCellCoords
                new_coords = action.impactedCoords
                self._check_for_mana_bubble(
                    player_game_info, new_coords.rowIndex, new_coords.columnIndex
                )
                move_cell(
                    original_coords.rowIndex,
                    original_coords.columnIndex,
                    new_coords.rowIndex,
                    new_coords.columnIndex,
                    self._board_array,
                )

            elif action_type == ActionType.CELL_ATTACK:
                attacking_coords = action.originatingCellCoords
                target_coords = action.impactedCoords
                trigger_cell_attack(
                    attacking_coords.rowIndex,
                    attacking_coords.columnIndex,
                    target_coords.rowIndex,
                    target_coords.columnIndex,
                    self._match_context,
                )

            elif action_type == ActionType.CELL_SPAWN:
                coords = action.impactedCoords
                self._check_for_mana_bubble(
                    player_game_info, coords.rowIndex, coords.columnIndex
                )
                spawn_cell(
                    coords.rowIndex,
                    coords.columnIndex,
                    action.player1,
                    self._board_array,
                )

            elif action_type == ActionType.PLAYER_SPELL:
                spell = get_spell(action.spellId)
                coords = action.impactedCoords
                spell.invoke(coords, self._board_array)

            return action
        except Exception:
            self._logger.critical(
                f"Failed to process the action : {action}", exc_info=True
            )
            return None

    def _process_player_mana(
        self, player_resources: PlayerResources, action: MatchActionDto
    ):
        """
        Processes the player mana regeneration.
        """
        if action.manaCost > player_resources.current_mp:
            raise ValueError(
                f"Player {action.player1} tried to perform an action with not enough mana."
            )

        player_resources.current_mp -= action.manaCost

    def _check_for_mana_bubble(
        self, player_game_info: PlayerResources, row_index: int, col_index: int
    ):
        """
        Increases the player's mana by one if the target cell is a mana bubble.
        """
        cell: Cell = self._board_array[row_index][col_index]
        if cell.is_mana_bubble():
            player_game_info.current_mp += 1
