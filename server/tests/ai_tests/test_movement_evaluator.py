from unittest.mock import MagicMock

import pytest

from ai.config.ai_config import EvaluationConstants, MovementWeights
from ai.strategy.evaluators.board.evaluation_constants import (
    MAX_THREAT_LEVEL, MIN_THREAT_LEVEL)
from ai.strategy.evaluators.movement_evaluator import MovementEvaluator
from game_engine.models.actions.cell_movement import CellMovement
from game_engine.models.cell.cell import Cell
from game_engine.models.dtos.coordinates import Coordinates
from game_engine.models.spells.spell_id import SpellId


class TestMovementEvaluator:
    """Tests for MovementEvaluator."""

    def _make_movement(self, source: Coordinates, dest: Coordinates) -> MagicMock:
        """Helper to create a mock CellMovement."""
        move = MagicMock(spec=CellMovement)
        move.metadata = MagicMock()
        move.metadata.originating_coords = source
        move.metadata.impacted_coords = dest
        return move

    def test_movement_closer_to_enemy_scores_higher(
        self, movement_evaluator: MovementEvaluator, board_evaluation: MagicMock
    ) -> None:
        """Destination closer to enemy master should score higher."""
        # Arrange
        near = self._make_movement(
            Coordinates(7, 5), Coordinates(8, 5)
        )  # dist 1 to enemy
        far = self._make_movement(
            Coordinates(4, 5), Coordinates(3, 5)
        )  # dist 6 to enemy

        # Act
        score_near = movement_evaluator.evaluate(near, board_evaluation)
        score_far = movement_evaluator.evaluate(far, board_evaluation)

        # Assert
        assert score_near > score_far

    def test_movement_equidistant_scores_equal_when_safe(
        self, movement_evaluator: MovementEvaluator, board_evaluation: MagicMock
    ) -> None:
        """Two destinations at equal distance from enemy master should score the same when not threatened."""
        # Arrange
        # Both dist 4 from enemy at (9,5)
        move_a = self._make_movement(Coordinates(4, 5), Coordinates(5, 5))  # dist 4
        move_b = self._make_movement(Coordinates(6, 3), Coordinates(7, 3))  # dist 4

        # Act
        score_a = movement_evaluator.evaluate(move_a, board_evaluation)
        score_b = movement_evaluator.evaluate(move_b, board_evaluation)

        # Assert
        assert score_a == pytest.approx(score_b)

    def test_movement_defensive_when_threatened(
        self, movement_evaluator: MovementEvaluator, board_evaluation: MagicMock
    ) -> None:
        """Under high threat, destinations closer to own master should score higher."""
        # Arrange
        board_evaluation.master_threat_level = MAX_THREAT_LEVEL

        # Both equidistant from enemy (9,5) at dist 7
        near_own = self._make_movement(
            Coordinates(1, 5), Coordinates(2, 5)
        )  # dist to own = 1
        far_own = self._make_movement(
            Coordinates(4, 8), Coordinates(5, 8)
        )  # dist to own = 7

        # Act
        score_near = movement_evaluator.evaluate(near_own, board_evaluation)
        score_far = movement_evaluator.evaluate(far_own, board_evaluation)

        # Assert
        assert score_near > score_far

    def test_movement_no_defensive_bonus_when_safe(
        self, movement_evaluator: MovementEvaluator, board_evaluation: MagicMock
    ) -> None:
        """When threat is below threshold, distance to own master should not affect score."""
        # Arrange
        board_evaluation.master_threat_level = MIN_THREAT_LEVEL

        # Same enemy distance, different own-master distance
        near_own = self._make_movement(
            Coordinates(1, 5), Coordinates(2, 5)
        )  # dist to own = 1
        far_own = self._make_movement(
            Coordinates(4, 8), Coordinates(5, 8)
        )  # dist to own = 7

        # Act
        score_near = movement_evaluator.evaluate(near_own, board_evaluation)
        score_far = movement_evaluator.evaluate(far_own, board_evaluation)

        # Assert
        assert score_near == pytest.approx(score_far)

    def test_movement_score_is_deterministic(
        self, movement_evaluator: MovementEvaluator, board_evaluation: MagicMock
    ) -> None:
        """Same input should always produce the same score."""
        # Arrange
        move = self._make_movement(Coordinates(4, 5), Coordinates(5, 5))

        # Act
        score1 = movement_evaluator.evaluate(move, board_evaluation)
        score2 = movement_evaluator.evaluate(move, board_evaluation)

        # Assert
        assert score1 == score2

    def test_movement_exact_score_at_enemy_master(
        self, movement_evaluator: MovementEvaluator, board_evaluation: MagicMock
    ) -> None:
        """Verify exact score computation for a destination adjacent to the enemy master."""
        # Arrange
        move = self._make_movement(
            Coordinates(7, 5), Coordinates(8, 5)
        )  # dist 1 to enemy

        # Act
        score = movement_evaluator.evaluate(move, board_evaluation)

        # Assert
        expected = (
            MovementWeights.BASE_SCORE
            + (EvaluationConstants.MAX_BOARD_DISTANCE - 1)
            * MovementWeights.DISTANCE_TO_ENEMY_MASTER
        )
        assert score == expected

    def test_movement_on_mana_bubble_bonus(
        self, movement_evaluator: MovementEvaluator, board_evaluation: MagicMock
    ) -> None:
        """Test that moving onto a mana bubble gives a critical bonus."""
        # Arrange
        move = self._make_movement(Coordinates(4, 5), Coordinates(5, 5))

        # Modify cells in the board directly
        source_cell = movement_evaluator._match_context.game_board.board[4][5]
        source_cell.is_archer.return_value = False
        dest_cell = movement_evaluator._match_context.game_board.board[5][5]
        dest_cell.is_mana_bubble.return_value = True

        # Act
        score = movement_evaluator.evaluate(move, board_evaluation)

        # Assert
        # Should include base + distance + MANA_BUBBLE_BONUS
        dist_to_enemy = 4  # (5,5) to (9,5)
        expected_base = (
            MovementWeights.BASE_SCORE
            + (EvaluationConstants.MAX_BOARD_DISTANCE - dist_to_enemy)
            * MovementWeights.DISTANCE_TO_ENEMY_MASTER
        )
        assert score >= expected_base + MovementWeights.MANA_BUBBLE_BONUS

    def test_movement_near_mana_bubble_bonus(
        self, movement_evaluator: MovementEvaluator, board_evaluation: MagicMock
    ) -> None:
        """Test that moving next to a mana bubble gives a strong bonus."""
        # Arrange
        move = self._make_movement(Coordinates(4, 5), Coordinates(5, 5))

        # Modify source cell
        source_cell = movement_evaluator._match_context.game_board.board[4][5]
        source_cell.is_archer.return_value = False

        # Build dest neighbors mock
        bubble_neighbor = MagicMock()
        bubble_neighbor.is_mana_bubble.return_value = True
        movement_evaluator._match_context.game_board.get_idle_neighbours.return_value = [
            bubble_neighbor
        ]

        # Act
        score = movement_evaluator.evaluate(move, board_evaluation)

        # Assert
        # Should include base + distance + MANA_BUBBLE_NEIGHBOR_BONUS
        dist_to_enemy = 4
        expected_base = (
            MovementWeights.BASE_SCORE
            + (EvaluationConstants.MAX_BOARD_DISTANCE - dist_to_enemy)
            * MovementWeights.DISTANCE_TO_ENEMY_MASTER
        )
        assert score >= expected_base + MovementWeights.MANA_BUBBLE_NEIGHBOR_BONUS

    def test_movement_near_enemy_archer_bonus(
        self, movement_evaluator: MovementEvaluator, board_evaluation: MagicMock
    ) -> None:
        """Test bonus for positioning next to an enemy archer."""
        # Arrange
        move = self._make_movement(Coordinates(4, 5), Coordinates(5, 5))

        # Modify source cell
        source_cell = movement_evaluator._match_context.game_board.board[4][5]
        source_cell.is_archer.return_value = False

        # Mock neighbors to contain an enemy archer
        enemy_archer = MagicMock()
        enemy_archer.is_owned.return_value = True
        enemy_archer.is_archer.return_value = True
        enemy_archer.belongs_to_player_1.return_value = False

        movement_evaluator._match_context.game_board.get_neighbours.return_value = [
            enemy_archer
        ]

        # Act
        score = movement_evaluator.evaluate(move, board_evaluation)

        # Assert
        assert (
            score
            >= MovementWeights.BASE_SCORE + MovementWeights.ENEMY_ARCHER_NEIGHBOR_BONUS
        )

    def test_movement_archer_creation_opportunity(
        self, movement_evaluator: MovementEvaluator, board_evaluation: MagicMock
    ) -> None:
        """Test bonus for moving into an isolated position if Archery Vow is available."""
        # Arrange
        move = self._make_movement(Coordinates(4, 5), Coordinates(5, 5))

        # Setup AI player with Archery Vow and Mana
        ai_player = movement_evaluator._match_context.player1
        ai_player.resources.spells = {SpellId.ARCHERY_VOW: 1}
        ai_player.resources.current_mp = 10

        # Modify source cell
        source_cell = movement_evaluator._match_context.game_board.board[4][5]
        source_cell.is_archer.return_value = False
        source_cell.is_master = False

        # Mock board behavior for isolated check
        movement_evaluator._match_context.game_board.get_owned_neighbours.return_value = (
            []
        )

        # Act
        score = movement_evaluator.evaluate(move, board_evaluation)

        # Assert
        assert (
            score >= MovementWeights.BASE_SCORE + MovementWeights.ARCHER_CREATION_BONUS
        )

    def test_movement_defensive_positioning_critical(
        self, movement_evaluator: MovementEvaluator, board_evaluation: MagicMock
    ) -> None:
        """Test extra bonus for defensive movement when master is critical."""
        # Arrange
        move = self._make_movement(
            Coordinates(1, 4), Coordinates(1, 5)
        )  # dist 0 to own master (1,5)

        # Mock player health to critical (2 HP)
        movement_evaluator._match_context.player1.resources.current_hp = 2

        # Modify source cell
        source_cell = movement_evaluator._match_context.game_board.board[1][4]
        source_cell.is_archer.return_value = False
        source_cell.is_master = False

        # Act
        score = movement_evaluator.evaluate(move, board_evaluation)

        # Assert
        assert score > MovementWeights.DEFENSIVE_POSITIONING

    def test_master_escape_movement_when_critical_and_not_stuck(
        self, movement_evaluator: MovementEvaluator, board_evaluation: MagicMock
    ) -> None:
        """Test that the master cell prioritizes moving away from enemies when it is critical."""
        # Arrange
        # Master is at (1, 5)
        # Move escape: (1, 5) -> (0, 5)
        move_escape = self._make_movement(Coordinates(1, 5), Coordinates(0, 5))

        # Mock player health to critical
        movement_evaluator._match_context.player1.resources.current_hp = 2

        # Master is NOT stuck (implied by board evaluations results or simply by evaluating movement)
        board_evaluation.is_ai_master_stuck = False

        # Modify source cell to be the master
        source_cell = movement_evaluator._match_context.game_board.board[1][5]
        source_cell.is_master = True

        # Need to mock get_cells_owned_by_player for enemies
        enemy_master = MagicMock(spec=Cell)
        enemy_master.row_index, enemy_master.column_index = 9, 5
        movement_evaluator._match_context.game_board.get_cells_owned_by_player.return_value = [
            enemy_master
        ]

        # Act
        score = movement_evaluator.evaluate(move_escape, board_evaluation)

        # Assert
        assert (
            score >= MovementWeights.BASE_SCORE + MovementWeights.MASTER_ESCAPE_BONUS
        )

    def test_master_prioritizes_escape_over_mana_bubble_spawn(
        self, movement_evaluator: MovementEvaluator, board_evaluation: MagicMock
    ) -> None:
        """Test that the master escape score is high enough to beat high-value spawns."""
        # Arrange
        # Master at (1, 5) moves to safety (0, 5)
        move_escape = self._make_movement(Coordinates(1, 5), Coordinates(0, 5))

        # Mock player health to critical
        movement_evaluator._match_context.player1.resources.current_hp = 2
        board_evaluation.is_ai_master_stuck = False

        # Master is the source
        source_cell = movement_evaluator._match_context.game_board.board[1][5]
        source_cell.is_master = True

        # Enemy at (2, 5)
        enemy_cell = MagicMock(spec=Cell)
        enemy_cell.row_index, enemy_cell.column_index = 2, 5
        movement_evaluator._match_context.game_board.get_cells_owned_by_player.return_value = [
            enemy_cell
        ]

        # Act
        escape_score = movement_evaluator.evaluate(move_escape, board_evaluation)

        # High-value spawn score calculation (for comparison)
        from ai.config.ai_config import SpawnWeights

        max_spawn_score = SpawnWeights.BASE_SCORE + SpawnWeights.MANA_BUBBLE_BONUS

        # Assert
        # Escape (Base 5 + Escape 130 + dist) should be > Spawn on bubble (Base 45 + 80 = 125)
        assert escape_score > max_spawn_score
