import pytest
from unittest.mock import MagicMock
from ai.strategy.evaluators.cell_evaluator import CellEvaluator
from ai.strategy.evaluators.board.board_evaluation import BoardEvaluation
from ai.strategy.evaluators.board.evaluation_constants import MIN_THREAT_LEVEL
from game_engine.models.dtos.coordinates import Coordinates
from game_engine.models.match.match_context import MatchContext
from handlers.match_handler_unit import MatchHandlerUnit


@pytest.fixture
def mock_match() -> MagicMock:
    match = MagicMock(spec=MatchHandlerUnit)
    match.match_context = MagicMock(spec=MatchContext)
    return match


@pytest.fixture
def evaluator(mock_match: MagicMock) -> CellEvaluator:
    return CellEvaluator(mock_match, ai_is_player1=True)


@pytest.fixture
def board_evaluation() -> BoardEvaluation:
    # Create a mock board evaluation
    # Player 1 Master at (1, 5)
    # Player 2 Master at (9, 5)
    eval_obj = MagicMock(spec=BoardEvaluation)
    eval_obj.ai_master_coords = Coordinates(1, 5)
    eval_obj.enemy_master_coords = Coordinates(9, 5)
    eval_obj.master_threat_level = MIN_THREAT_LEVEL
    return eval_obj
