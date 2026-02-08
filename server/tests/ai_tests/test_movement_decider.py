import pytest
from typing import Optional
from unittest.mock import MagicMock, patch
from ai.strategy.decision_makers.movement_decider import MovementDecider
from ai.strategy.evaluators.board.board_evaluation import BoardEvaluation
from ai.strategy.evaluators.board.evaluation_constants import MIN_THREAT_LEVEL
from game_engine.models.actions.cell_movement import CellMovement
from game_engine.models.actions.cell_attack import CellAttack
from game_engine.models.dtos.coordinates import Coordinates
from game_engine.models.match.match_context import MatchContext
from game_engine.models.game_board import GameBoard


class TestMovementDecider:
    @pytest.fixture
    def mock_match(self) -> MagicMock:
        match = MagicMock()
        match.match_context = MagicMock(spec=MatchContext)
        match.match_context.game_board = MagicMock(spec=GameBoard)
        return match

    @pytest.fixture
    def decider(self, mock_match: MagicMock) -> MovementDecider:
        return MovementDecider(mock_match, ai_is_player1=True)

    @pytest.fixture
    def board_evaluation(self) -> MagicMock:
        eval_obj = MagicMock(spec=BoardEvaluation)
        eval_obj.ai_master_coords = Coordinates(1, 5)
        eval_obj.enemy_master_coords = Coordinates(9, 5)
        eval_obj.master_threat_level = MIN_THREAT_LEVEL
        return eval_obj

    def _make_movement(self, origin: Coordinates, target: Coordinates) -> MagicMock:
        """Helper to create a mock CellMovement with the given coordinates."""
        move = MagicMock(spec=CellMovement)
        move.metadata = MagicMock()
        move.metadata.originating_coords = origin
        move.metadata.impacted_coords = target
        return move

    @patch(
        "ai.strategy.decision_makers.movement_decider.get_possible_movements_and_attacks"
    )
    def test_picks_movement_closer_to_enemy_master(
        self,
        mock_get_options: MagicMock,
        decider: MovementDecider,
        mock_match: MagicMock,
        board_evaluation: MagicMock,
    ) -> None:
        """The decider should prefer a move that gets closer to the enemy master."""
        # Arrange
        cell: MagicMock = MagicMock()
        mock_match.match_context.game_board.get_cells_owned_by_player.return_value = [
            cell
        ]

        move_forward: MagicMock = self._make_movement(
            Coordinates(5, 5), Coordinates(6, 5)
        )
        move_backward: MagicMock = self._make_movement(
            Coordinates(5, 5), Coordinates(4, 5)
        )
        mock_get_options.return_value = {move_forward, move_backward}

        # Act
        action: Optional[CellMovement] = decider.decide_movement(board_evaluation)

        # Assert — move to (6,5) is closer to enemy at (9,5)
        assert action.action == move_forward

    @patch(
        "ai.strategy.decision_makers.movement_decider.get_possible_movements_and_attacks"
    )
    def test_returns_none_when_no_movements(
        self,
        mock_get_options: MagicMock,
        decider: MovementDecider,
        mock_match: MagicMock,
        board_evaluation: MagicMock,
    ) -> None:
        """Returns None when no movement options exist."""
        # Arrange
        cell: MagicMock = MagicMock()
        mock_match.match_context.game_board.get_cells_owned_by_player.return_value = [
            cell
        ]
        mock_get_options.return_value = set()

        # Act
        action: Optional[CellMovement] = decider.decide_movement(board_evaluation)

        # Assert
        assert action is None

    @patch(
        "ai.strategy.decision_makers.movement_decider.get_possible_movements_and_attacks"
    )
    def test_returns_none_when_no_cells(
        self,
        mock_get_options: MagicMock,
        decider: MovementDecider,
        mock_match: MagicMock,
        board_evaluation: MagicMock,
    ) -> None:
        """Returns None when AI has no cells on the board."""
        # Arrange
        mock_match.match_context.game_board.get_cells_owned_by_player.return_value = []

        # Act
        action: Optional[CellMovement] = decider.decide_movement(board_evaluation)

        # Assert
        assert action is None
        mock_get_options.assert_not_called()

    @patch(
        "ai.strategy.decision_makers.movement_decider.get_possible_movements_and_attacks"
    )
    def test_filters_out_attacks_only_returns_movements(
        self,
        mock_get_options: MagicMock,
        decider: MovementDecider,
        mock_match: MagicMock,
        board_evaluation: MagicMock,
    ) -> None:
        """Attacks returned by get_possible_movements_and_attacks should be ignored."""
        # Arrange
        cell: MagicMock = MagicMock()
        mock_match.match_context.game_board.get_cells_owned_by_player.return_value = [
            cell
        ]

        attack: MagicMock = MagicMock(spec=CellAttack)
        move: MagicMock = self._make_movement(Coordinates(5, 5), Coordinates(6, 5))
        mock_get_options.return_value = {attack, move}

        # Act
        action: Optional[CellMovement] = decider.decide_movement(board_evaluation)

        # Assert
        assert action.action == move

    @patch(
        "ai.strategy.decision_makers.movement_decider.get_possible_movements_and_attacks"
    )
    def test_returns_none_when_only_attacks_available(
        self,
        mock_get_options: MagicMock,
        decider: MovementDecider,
        mock_match: MagicMock,
        board_evaluation: MagicMock,
    ) -> None:
        """Returns None when options contain only attacks and no movements."""
        # Arrange
        cell: MagicMock = MagicMock()
        mock_match.match_context.game_board.get_cells_owned_by_player.return_value = [
            cell
        ]

        attack: MagicMock = MagicMock(spec=CellAttack)
        mock_get_options.return_value = {attack}

        # Act
        action: Optional[CellMovement] = decider.decide_movement(board_evaluation)

        # Assert
        assert action is None

    @patch(
        "ai.strategy.decision_makers.movement_decider.get_possible_movements_and_attacks"
    )
    def test_considers_all_cells(
        self,
        mock_get_options: MagicMock,
        decider: MovementDecider,
        mock_match: MagicMock,
        board_evaluation: MagicMock,
    ) -> None:
        """Movements from all AI cells should be considered, picking the best overall."""
        # Arrange
        cell_a: MagicMock = MagicMock()
        cell_b: MagicMock = MagicMock()
        mock_match.match_context.game_board.get_cells_owned_by_player.return_value = [
            cell_a,
            cell_b,
        ]

        # Cell A can only move sideways (no progress toward enemy at 9,5)
        move_a: MagicMock = self._make_movement(Coordinates(3, 5), Coordinates(3, 4))
        # Cell B can move forward (closer to enemy)
        move_b: MagicMock = self._make_movement(Coordinates(7, 5), Coordinates(8, 5))

        mock_get_options.side_effect = [{move_a}, {move_b}]

        # Act
        action: Optional[CellMovement] = decider.decide_movement(board_evaluation)

        # Assert — move_b at (8,5) is much closer to enemy (9,5) than move_a at (3,4)
        assert action.action == move_b

    @patch(
        "ai.strategy.decision_makers.movement_decider.get_possible_movements_and_attacks"
    )
    def test_uses_transient_board(
        self,
        mock_get_options: MagicMock,
        decider: MovementDecider,
        mock_match: MagicMock,
        board_evaluation: MagicMock,
    ) -> None:
        """get_possible_movements_and_attacks should be called with a cloned transient board."""
        # Arrange
        transient_board: MagicMock = MagicMock(spec=GameBoard)
        mock_match.match_context.game_board.clone_as_transient.return_value = (
            transient_board
        )

        cell: MagicMock = MagicMock()
        mock_match.match_context.game_board.get_cells_owned_by_player.return_value = [
            cell
        ]
        mock_get_options.return_value = set()

        # Act
        decider.decide_movement(board_evaluation)

        # Assert
        mock_get_options.assert_called_once_with(
            True, cell, transient_board, mock_match.turn_state
        )

    @patch(
        "ai.strategy.decision_makers.movement_decider.get_possible_movements_and_attacks"
    )
    def test_single_movement_option_is_returned(
        self,
        mock_get_options: MagicMock,
        decider: MovementDecider,
        mock_match: MagicMock,
        board_evaluation: MagicMock,
    ) -> None:
        """When only one movement is available, it should be returned."""
        # Arrange
        cell: MagicMock = MagicMock()
        mock_match.match_context.game_board.get_cells_owned_by_player.return_value = [
            cell
        ]

        only_move: MagicMock = self._make_movement(Coordinates(5, 5), Coordinates(6, 5))
        mock_get_options.return_value = {only_move}

        # Act
        action: Optional[CellMovement] = decider.decide_movement(board_evaluation)

        # Assert
        assert action.action == only_move

    @patch(
        "ai.strategy.decision_makers.movement_decider.get_possible_movements_and_attacks"
    )
    def test_delegates_scoring_to_evaluator(
        self,
        mock_get_options: MagicMock,
        decider: MovementDecider,
        mock_match: MagicMock,
        board_evaluation: MagicMock,
    ) -> None:
        """The decider should use MovementEvaluator.evaluate for scoring."""
        # Arrange
        cell: MagicMock = MagicMock()
        mock_match.match_context.game_board.get_cells_owned_by_player.return_value = [
            cell
        ]

        move_a: MagicMock = self._make_movement(Coordinates(5, 5), Coordinates(6, 5))
        move_b: MagicMock = self._make_movement(Coordinates(5, 5), Coordinates(4, 5))
        mock_get_options.return_value = {move_a, move_b}

        # Rig the evaluator to prefer move_b (score 100 vs 50)
        with patch.object(decider._evaluator, "evaluate") as mock_eval:
            mock_eval.side_effect = lambda coords, _: (
                50.0 if coords == move_a.metadata.impacted_coords else 100.0
            )

            # Act
            action: Optional[CellMovement] = decider.decide_movement(board_evaluation)

            # Assert
            assert action.action == move_b
            assert mock_eval.call_count == 2
