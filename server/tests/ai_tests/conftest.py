from unittest.mock import MagicMock

import pytest

from ai.strategy.evaluators.attack_evaluator import AttackEvaluator
from ai.strategy.evaluators.board.board_evaluation import BoardEvaluation
from ai.strategy.evaluators.board.evaluation_constants import MIN_THREAT_LEVEL
from ai.strategy.evaluators.movement_evaluator import MovementEvaluator
from ai.strategy.evaluators.spawn_evaluator import SpawnEvaluator
from game_engine.models.dtos.coordinates import Coordinates
from game_engine.models.game_board import GameBoard
from game_engine.models.match.match_context import MatchContext
from game_engine.models.player.player import Player
from game_engine.models.player.player_resources import PlayerResources
from handlers.match_handler_unit import MatchHandlerUnit


@pytest.fixture
def mock_match() -> MagicMock:
    match = MagicMock(spec=MatchHandlerUnit)
    match_context = MagicMock(spec=MatchContext)
    match.match_context = match_context

    # Add turn_state for movement decider tests
    match.turn_state = MagicMock()

    # Ensure game_board is accessible on both match and match_context
    game_board = MagicMock(spec=GameBoard)
    # Create mock cells with is_mana_bubble() returning False by default
    board_cells = []
    for i in range(11):
        row = []
        for j in range(11):
            cell = MagicMock()
            cell.is_mana_bubble.return_value = False
            cell.is_archer.return_value = False  # Default: cells are not archers
            cell.is_shielded.return_value = False
            row.append(cell)
        board_cells.append(row)
    game_board.board = board_cells
    # Make get() return the appropriate cell
    game_board.get = lambda r, c: board_cells[r][c]
    # Make get_owned_neighbours return empty list by default
    game_board.get_owned_neighbours.return_value = []
    match.game_board = game_board
    match_context.game_board = game_board

    # Mock players with resources
    player1 = MagicMock(spec=Player)
    player1.resources = MagicMock(spec=PlayerResources)
    player1.resources.spells = {}  # Empty spell dict by default
    player1.resources.current_mp = 5
    player1.resources.current_hp = 5  # Default health
    match_context.player1 = player1

    player2 = MagicMock(spec=Player)
    player2.resources = MagicMock(spec=PlayerResources)
    player2.resources.spells = {}  # Empty spell dict by default
    player2.resources.current_mp = 5
    player2.resources.current_hp = 5  # Default health
    match_context.player2 = player2

    return match


@pytest.fixture
def spawn_evaluator(mock_match: MagicMock) -> SpawnEvaluator:
    return SpawnEvaluator(mock_match, ai_is_player1=True)


@pytest.fixture
def attack_evaluator(mock_match: MagicMock) -> AttackEvaluator:
    return AttackEvaluator(mock_match, ai_is_player1=True)


@pytest.fixture
def movement_evaluator(mock_match: MagicMock) -> MovementEvaluator:
    return MovementEvaluator(mock_match, ai_is_player1=True)


@pytest.fixture
def board_evaluation() -> BoardEvaluation:
    # Create a mock board evaluation
    # Player 1 Master at (1, 5)
    # Player 2 Master at (9, 5)
    eval_obj = MagicMock(spec=BoardEvaluation)
    eval_obj.ai_master_coords = Coordinates(1, 5)
    eval_obj.enemy_master_coords = Coordinates(9, 5)
    eval_obj.master_threat_level = MIN_THREAT_LEVEL
    eval_obj.is_ai_master_stuck = False
    eval_obj.ai_mp = 5
    eval_obj.ai_stamina = 10
    eval_obj.positional_advantage = 0
    eval_obj.enemy_cell_clusters = []
    eval_obj.current_turn = 10  # Default to mid-game
    eval_obj.ai_master_in_critical_danger.return_value = False
    eval_obj.ai_is_losing.return_value = False
    return eval_obj
