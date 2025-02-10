from dto.coordinates_dto import CoordinatesDto
from game_engine.models.actions.action import Action
from game_engine.models.actions.cell_movement import CellMovement
from game_engine.models.actions.cell_spawn import CellSpawn
from game_engine.models.cell.cell import Cell
from game_engine.models.game_board import GameBoard
from game_engine.models.match_context import MatchContext
from game_engine.models.player_resources import PlayerResources


def process_action(action: Action, match_context: MatchContext) -> Action:
    player_resources = match_context.get_player_resources(action.from_player1)

    _process_player_mana(player_resources, action)

    if isinstance(action, (CellMovement, CellSpawn)):
        game_board = match_context.game_board
        _check_for_mana_bubble(player_resources, game_board, action.impacted_coords)

    action.apply(match_context)

    return action


def _process_player_mana(player_resources: PlayerResources, action: Action):
    """
    Processes the player mana regeneration.
    """
    if action.mana_cost > player_resources.current_mp:
        raise ValueError(f"Tried to perform an action with not enough mana.")

    player_resources.current_mp -= action.mana_cost


def _check_for_mana_bubble(
    player_resources: PlayerResources,
    game_board: GameBoard,
    coords: CoordinatesDto,
):
    """
    Increases the player's mana by one if the target cell is a mana bubble.
    """
    cell: Cell = game_board.get(coords.rowIndex, coords.columnIndex)
    if cell.is_mana_bubble():
        player_resources.current_mp += 1
