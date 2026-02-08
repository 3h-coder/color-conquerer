import pytest
from typing import Optional
from unittest.mock import MagicMock, patch
from ai.strategy.decision_makers.attack_decider import AttackDecider
from ai.strategy.evaluators.board.board_evaluation import BoardEvaluation
from game_engine.models.actions.cell_attack import CellAttack
from game_engine.models.dtos.coordinates import Coordinates
from game_engine.models.match.match_context import MatchContext
from game_engine.models.cell.cell import Cell
from handlers.match_handler_unit import MatchHandlerUnit
from game_engine.models.game_board import GameBoard


class TestAttackDecider:
    @pytest.fixture
    def mock_match(self) -> MagicMock:
        match: MagicMock = MagicMock(spec=MatchHandlerUnit)
        match.match_context = MagicMock(spec=MatchContext)
        match.match_context.game_board = MagicMock(spec=GameBoard)
        match.turn_state = MagicMock()
        return match

    @pytest.fixture
    def decider(self, mock_match: MagicMock) -> AttackDecider:
        return AttackDecider(mock_match, ai_is_player1=True)

    @patch(
        "ai.strategy.decision_makers.attack_decider.get_possible_movements_and_attacks"
    )
    def test_decide_attack_no_options(
        self, mock_get_options: MagicMock, decider: AttackDecider
    ) -> None:
        # Arrange
        mock_get_options.return_value = set()
        evaluation: BoardEvaluation = MagicMock(spec=BoardEvaluation)

        # Ensure game_board.get_cells_owned_by_player is mocked
        decider._match_context.game_board.get_cells_owned_by_player.return_value = [
            MagicMock(spec=Cell)
        ]

        # Act
        action: Optional[CellAttack] = decider.decide_attack(evaluation)

        # Assert
        assert action is None

    @patch(
        "ai.strategy.decision_makers.attack_decider.get_possible_movements_and_attacks"
    )
    def test_decide_attack_picks_best_score(
        self, mock_get_options: MagicMock, decider: AttackDecider, mock_match: MagicMock
    ) -> None:
        # Arrange
        evaluation: BoardEvaluation = MagicMock(spec=BoardEvaluation)

        ai_cell: Cell = MagicMock(spec=Cell)
        mock_match.match_context.game_board.get_cells_owned_by_player.return_value = [
            ai_cell
        ]

        attack1: CellAttack = MagicMock(spec=CellAttack)
        attack1.metadata = MagicMock()
        attack1.metadata.impacted_coords = Coordinates(8, 5)

        attack2: CellAttack = MagicMock(spec=CellAttack)
        attack2.metadata = MagicMock()
        attack2.metadata.impacted_coords = Coordinates(4, 5)

        mock_get_options.return_value = {attack1, attack2}

        # Mock the evaluator to prefer attack2
        with patch.object(decider._cell_evaluator, "evaluate_target_cell") as mock_eval:
            mock_eval.side_effect = lambda coords, _: (
                100.0 if coords == attack1.metadata.impacted_coords else 200.0
            )

            # Act
            action: Optional[CellAttack] = decider.decide_attack(evaluation)

            # Assert
            assert action == attack2

    @patch(
        "ai.strategy.decision_makers.attack_decider.get_possible_movements_and_attacks"
    )
    def test_decide_attack_returns_none_if_no_cells(
        self, mock_get_options: MagicMock, decider: AttackDecider, mock_match: MagicMock
    ) -> None:
        """Test that None is returned if AI has no cells on board."""
        # Arrange
        mock_match.match_context.game_board.get_cells_owned_by_player.return_value = []
        evaluation: BoardEvaluation = MagicMock(spec=BoardEvaluation)

        # Act
        action: Optional[CellAttack] = decider.decide_attack(evaluation)

        # Assert
        assert action is None
