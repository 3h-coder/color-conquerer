"""
Unit tests for the BoardEvaluator class.

These tests construct specific game board scenarios and verify the evaluation results.
"""

from unittest.mock import MagicMock

import pytest

from ai.strategy.evaluators.board.board_evaluator import BoardEvaluator
from ai.strategy.evaluators.board.evaluation_constants import (
    CRITICAL_HP_THRESHOLD, LOSING_CELL_DISADVANTAGE_THRESHOLD,
    MIN_THREAT_LEVEL, WINNING_CELL_ADVANTAGE_THRESHOLD)
from constants.game_constants import BOARD_SIZE
from game_engine.models.cell.cell import Cell
from game_engine.models.cell.cell_owner import CellOwner
from game_engine.models.cell.cell_state import CellState
from game_engine.models.game_board import GameBoard
from game_engine.models.match.match_context import MatchContext
from game_engine.models.player.player import Player
from game_engine.models.player.player_match_data import PlayerMatchData
from game_engine.models.player.player_resources import PlayerResources
from handlers.match_handler_unit import MatchHandlerUnit


class TestBoardEvaluator:
    """Test suite for BoardEvaluator functionality."""

    def _get_evaluator(
        self, match_context: MatchContext, ai_is_player1: bool = True
    ) -> BoardEvaluator:
        """Helper to create a BoardEvaluator with a specific context."""
        mock_match = MagicMock(spec=MatchHandlerUnit)
        mock_match.match_context = match_context
        return BoardEvaluator(mock_match, ai_is_player1)

    def test_initial_board_evaluation(self) -> None:
        """Test evaluation of an initial game board with just master cells."""
        # === Arrange ===
        match_context = create_test_match_context()
        evaluator = self._get_evaluator(match_context)

        # === Act ===
        evaluation = evaluator.evaluate()

        # === Assert ===
        # Both players should have 1 cell (their master)
        assert evaluation.ai_cell_count == 1
        assert evaluation.enemy_cell_count == 1
        assert evaluation.cell_control_advantage == 0

        # No immediate threats at game start
        assert evaluation.master_threat_level == MIN_THREAT_LEVEL
        assert len(evaluation.enemy_cells_near_ai_master) == 0
        assert len(evaluation.ai_cells_near_enemy_master) == 0

        # Both players start with full HP
        assert evaluation.ai_hp == evaluation.enemy_hp

    def test_cell_control_advantage(self) -> None:
        """Test that cell control advantage is calculated correctly."""
        # === Arrange ===
        match_context = create_test_match_context()
        board = match_context.game_board

        # Give AI 3 additional cells
        spawn_cell(board, 2, 5, CellOwner.PLAYER_1)
        spawn_cell(board, 3, 5, CellOwner.PLAYER_1)
        spawn_cell(board, 3, 6, CellOwner.PLAYER_1)

        # Give enemy 1 additional cell
        spawn_cell(board, 8, 5, CellOwner.PLAYER_2)

        evaluator = self._get_evaluator(match_context)

        # === Act ===
        evaluation = evaluator.evaluate()

        # === Assert ===
        assert evaluation.ai_cell_count == 4  # Master + 3 spawned
        assert evaluation.enemy_cell_count == 2  # Master + 1 spawned
        assert evaluation.cell_control_advantage == 2

    def test_threat_detection_adjacent_enemies(self) -> None:
        """Test that adjacent enemy cells are detected as threats."""
        # === Arrange ===
        match_context = create_test_match_context()
        board = match_context.game_board

        # Place enemy cells near AI master (row 1, col 5)
        spawn_cell(board, 1, 4, CellOwner.PLAYER_2)  # Left of AI master
        spawn_cell(board, 2, 5, CellOwner.PLAYER_2)  # Below AI master

        evaluator = self._get_evaluator(match_context)

        # === Act ===
        evaluation = evaluator.evaluate()

        # === Assert ===
        assert len(evaluation.enemy_cells_near_ai_master) == 2
        assert evaluation.master_threat_level > 0

    def test_archer_threat_from_distance(self) -> None:
        """Test that archer cells are considered threats even from far away."""
        # === Arrange ===
        match_context = create_test_match_context()
        board = match_context.game_board

        # Place an archer cell far from AI master
        archer_cell = spawn_cell(board, 8, 8, CellOwner.PLAYER_2)
        archer_cell.add_modifier(CellState.ARCHER)

        evaluator = self._get_evaluator(match_context)

        # === Act ===
        evaluation = evaluator.evaluate()

        # === Assert ===
        # Archer should not be in "near" list (it's far away)
        assert len(evaluation.enemy_cells_near_ai_master) == 0

        # But threat level should still be elevated due to archer
        assert evaluation.master_threat_level > 0

    def test_master_stuck_detection(self) -> None:
        """Test that the evaluator correctly identifies if the AI master is stuck."""
        # === Arrange ===
        match_context = create_test_match_context()
        board = match_context.game_board

        # AI Master is at (1, 5)
        # Surround AI Master with enemy cells
        spawn_cell(board, 0, 4, CellOwner.PLAYER_2)
        spawn_cell(board, 0, 5, CellOwner.PLAYER_2)
        spawn_cell(board, 0, 6, CellOwner.PLAYER_2)
        spawn_cell(board, 1, 4, CellOwner.PLAYER_2)
        spawn_cell(board, 1, 6, CellOwner.PLAYER_2)
        spawn_cell(board, 2, 4, CellOwner.PLAYER_2)
        spawn_cell(board, 2, 5, CellOwner.PLAYER_2)
        spawn_cell(board, 2, 6, CellOwner.PLAYER_2)

        evaluator = self._get_evaluator(match_context)

        # === Act ===
        evaluation = evaluator.evaluate()

        # === Assert ===
        assert evaluation.is_ai_master_stuck is True

    def test_master_not_stuck_with_idle_neighbor(self) -> None:
        """Test that the evaluator correctly identifies the master is NOT stuck if there is an idle spot."""
        # === Arrange ===
        match_context = create_test_match_context()
        board = match_context.game_board

        # AI Master is at (1, 5). Surround with enemy cells EXCEPT (0, 5)
        spawn_cell(board, 0, 4, CellOwner.PLAYER_2)
        # (0, 5) remains idle
        spawn_cell(board, 0, 6, CellOwner.PLAYER_2)
        spawn_cell(board, 1, 4, CellOwner.PLAYER_2)
        spawn_cell(board, 1, 6, CellOwner.PLAYER_2)
        spawn_cell(board, 2, 4, CellOwner.PLAYER_2)
        spawn_cell(board, 2, 5, CellOwner.PLAYER_2)
        spawn_cell(board, 2, 6, CellOwner.PLAYER_2)

        evaluator = self._get_evaluator(match_context)

        # === Act ===
        evaluation = evaluator.evaluate()

        # === Assert ===
        assert evaluation.is_ai_master_stuck is False

    def test_lethal_opportunity_detection(self) -> None:
        """Test detection of lethal opportunities when AI can kill enemy master."""
        # === Arrange ===
        match_context = create_test_match_context()
        board = match_context.game_board

        # Reduce enemy HP to 2
        match_context.player2.resources.current_hp = 2

        # Place 2 AI cells adjacent to enemy master (row 9, col 5)
        spawn_cell(board, 9, 4, CellOwner.PLAYER_1)  # Left of enemy master
        spawn_cell(board, 8, 5, CellOwner.PLAYER_1)  # Above enemy master

        evaluator = self._get_evaluator(match_context)

        # === Act ===
        evaluation = evaluator.evaluate()

        # === Assert ===
        # 2 cells × 1 damage each = 2 damage, which equals enemy HP
        assert evaluation.ai_has_lethal_opportunity()

    def test_no_lethal_opportunity_insufficient_damage(self) -> None:
        """Test that lethal opportunity is not detected when damage is insufficient."""
        # === Arrange ===
        match_context = create_test_match_context()
        board = match_context.game_board

        # Enemy has 5 HP
        match_context.player2.resources.current_hp = 5

        # Place only 2 AI cells near enemy master
        spawn_cell(board, 9, 4, CellOwner.PLAYER_1)
        spawn_cell(board, 8, 5, CellOwner.PLAYER_1)

        evaluator = self._get_evaluator(match_context)

        # === Act ===
        evaluation = evaluator.evaluate()

        # === Assert ===
        # 2 cells × 1 damage = 2 damage, which is less than 5 HP
        assert not evaluation.ai_has_lethal_opportunity()

    def test_lethal_opportunity_with_archers(self) -> None:
        """Test lethal opportunity calculation includes distant archers."""
        # === Arrange ===
        match_context = create_test_match_context()
        board = match_context.game_board

        # Enemy has 3 HP
        match_context.player2.resources.current_hp = 3

        # Place 1 adjacent cell and 2 archers far away
        spawn_cell(board, 8, 5, CellOwner.PLAYER_1)
        archer1 = spawn_cell(board, 5, 5, CellOwner.PLAYER_1)
        archer1.add_modifier(CellState.ARCHER)
        archer2 = spawn_cell(board, 6, 6, CellOwner.PLAYER_1)
        archer2.add_modifier(CellState.ARCHER)

        evaluator = self._get_evaluator(match_context)

        # === Act ===
        evaluation = evaluator.evaluate()

        # === Assert ===
        # 3 cells that can attack × 1 damage = 3 damage = enemy HP
        assert evaluation.ai_has_lethal_opportunity()
        assert len(evaluation.ai_cells_that_can_attack_enemy_master) == 3

    def test_critical_danger_detection(self) -> None:
        """Test detection of critical danger to AI master."""
        # === Arrange ===
        match_context = create_test_match_context()
        board = match_context.game_board

        # Reduce AI HP to critical level
        match_context.player1.resources.current_hp = CRITICAL_HP_THRESHOLD

        # Place multiple enemies near AI master
        spawn_cell(board, 1, 4, CellOwner.PLAYER_2)
        spawn_cell(board, 2, 5, CellOwner.PLAYER_2)
        spawn_cell(board, 1, 6, CellOwner.PLAYER_2)

        evaluator = self._get_evaluator(match_context)

        # === Act ===
        evaluation = evaluator.evaluate()

        # === Assert ===
        assert evaluation.ai_master_in_critical_danger()

    def test_winning_position_detection(self) -> None:
        """Test detection of winning position."""
        # === Arrange ===
        match_context = create_test_match_context()
        board = match_context.game_board

        # Give AI significant cell advantage
        for i in range(WINNING_CELL_ADVANTAGE_THRESHOLD + 2):
            spawn_cell(board, 2 + i, 5, CellOwner.PLAYER_1)

        # AI has more HP
        match_context.player1.resources.current_hp = 10
        match_context.player2.resources.current_hp = 7

        evaluator = self._get_evaluator(match_context)

        # === Act ===
        evaluation = evaluator.evaluate()

        # === Assert ===
        assert evaluation.ai_is_winning()

    def test_losing_position_detection(self) -> None:
        """Test detection of losing position."""
        # === Arrange ===
        match_context = create_test_match_context()
        board = match_context.game_board

        # Give enemy significant cell advantage (spread across board to avoid out of bounds)
        # LOSING_CELL_DISADVANTAGE_THRESHOLD is e.g. -3.
        # We need AI_CELLS - ENEMY_CELLS <= -3
        # AI has 1 (master). So 1 - ENEMY_CELLS <= -3 => ENEMY_CELLS >= 4.
        # Enemy already has 1 (master). So spawn at least 3 more.
        num_to_spawn = abs(LOSING_CELL_DISADVANTAGE_THRESHOLD) + 1
        for i in range(num_to_spawn):
            spawn_cell(board, 7, i, CellOwner.PLAYER_2)

        # Enemy has more HP
        match_context.player1.resources.current_hp = 6
        match_context.player2.resources.current_hp = 10

        evaluator = self._get_evaluator(match_context)

        # === Act ===
        evaluation = evaluator.evaluate()

        # === Assert ===
        assert evaluation.ai_is_losing()

    def test_positional_advantage_calculation(self) -> None:
        """Test that positional advantage is calculated correctly."""
        # === Arrange ===
        match_context = create_test_match_context()
        board = match_context.game_board

        # Place AI cells closer to enemy master
        spawn_cell(board, 7, 5, CellOwner.PLAYER_1)
        spawn_cell(board, 6, 5, CellOwner.PLAYER_1)

        # Place enemy cells far from AI master
        spawn_cell(board, 5, 9, CellOwner.PLAYER_2)
        spawn_cell(board, 6, 9, CellOwner.PLAYER_2)

        evaluator = self._get_evaluator(match_context)

        # === Act ===
        evaluation = evaluator.evaluate()

        # === Assert ===
        # Positive positional advantage means AI is closer to enemy
        assert evaluation.positional_advantage > 0

    def test_enemy_clustering_detection(self) -> None:
        """Test detection of enemy cell clusters (useful for AoE spells)."""
        # === Arrange ===
        match_context = create_test_match_context()
        board = match_context.game_board

        # Create a cluster of 4 adjacent enemy cells
        spawn_cell(board, 7, 5, CellOwner.PLAYER_2)
        spawn_cell(board, 7, 6, CellOwner.PLAYER_2)
        spawn_cell(board, 8, 5, CellOwner.PLAYER_2)
        spawn_cell(board, 8, 6, CellOwner.PLAYER_2)

        # Create an isolated enemy cell
        spawn_cell(board, 6, 9, CellOwner.PLAYER_2)

        evaluator = self._get_evaluator(match_context)

        # === Act ===
        evaluation = evaluator.evaluate()

        # === Assert ===
        # Should detect 2 clusters (one with 4 cells, one with 1 cell)
        # Note: enemy master might form its own cluster if it has no neighbors
        assert len(evaluation.enemy_cell_clusters) >= 2
        assert evaluation.largest_enemy_cluster_size == 4

    def test_threat_level_increases_with_low_hp(self) -> None:
        """Test that threat level increases when HP is low."""
        # === Arrange ===
        match_context = create_test_match_context()
        board = match_context.game_board

        # Place the same enemy near AI master
        spawn_cell(board, 2, 5, CellOwner.PLAYER_2)

        # === Act ===
        # Test with high HP
        match_context.player1.resources.current_hp = 10
        evaluator_high = self._get_evaluator(match_context)
        evaluation_high_hp = evaluator_high.evaluate()

        # Test with low HP
        match_context.player1.resources.current_hp = 2
        evaluator_low = self._get_evaluator(match_context)
        evaluation_low_hp = evaluator_low.evaluate()

        # === Assert ===
        # Threat should be higher when HP is low
        assert (
            evaluation_low_hp.master_threat_level
            > evaluation_high_hp.master_threat_level
        )

    def test_ai_as_player2(self) -> None:
        """Test evaluation works correctly when AI is player 2."""
        # === Arrange ===
        match_context = create_test_match_context()
        board = match_context.game_board

        # Give player 2 (AI) more cells
        spawn_cell(board, 7, 5, CellOwner.PLAYER_2)
        spawn_cell(board, 8, 5, CellOwner.PLAYER_2)

        evaluator = self._get_evaluator(match_context, ai_is_player1=False)

        # === Act ===
        evaluation = evaluator.evaluate()

        # === Assert ===
        assert evaluation.ai_cell_count == 3  # Master + 2 spawned
        assert evaluation.enemy_cell_count == 1  # Just master
        assert evaluation.cell_control_advantage == 2
        assert evaluation.ai_master_cell.belongs_to_player_2()
        assert evaluation.enemy_master_cell.belongs_to_player_1()

    def test_master_cells_excluded_from_attack_calculations(self) -> None:
        """Test that master cells are not counted as potential attackers."""
        # === Arrange ===
        match_context = create_test_match_context()
        # Only master cells exist, no other units

        evaluator = self._get_evaluator(match_context)

        # === Act ===
        evaluation = evaluator.evaluate()

        # === Assert ===
        # Master cells should not be able to attack
        assert len(evaluation.ai_cells_that_can_attack_enemy_master) == 0

    def test_adjacent_melee_cells_can_attack(self) -> None:
        """Test that non-archer cells must be adjacent to attack."""
        # === Arrange ===
        match_context = create_test_match_context()
        board = match_context.game_board

        # Place a non-archer cell adjacent to enemy master
        adjacent_cell = spawn_cell(board, 8, 5, CellOwner.PLAYER_1)

        # Place a non-archer cell 2 spaces away from enemy master
        spawn_cell(board, 7, 5, CellOwner.PLAYER_1)

        evaluator = self._get_evaluator(match_context)

        # === Act ===
        evaluation = evaluator.evaluate()

        # === Assert ===
        # Only the adjacent cell should be able to attack
        assert len(evaluation.ai_cells_that_can_attack_enemy_master) == 1
        assert evaluation.ai_cells_that_can_attack_enemy_master[0] == adjacent_cell


# Helper functions for creating test scenarios


def create_test_match_context() -> MatchContext:
    """
    Creates a basic match context for testing with:
    - Empty board except for two master cells at standard positions
    - Both players at full health and resources
    """
    board = create_empty_board()

    # Place master cells at standard positions
    player1_master = board.get(1, 5)
    player1_master.set_owned_by_player1()
    player1_master.is_master = True

    player2_master = board.get(9, 5)
    player2_master.set_owned_by_player2()
    player2_master.is_master = True

    return MatchContext(
        id="test-match",
        room_id="test-room",
        current_turn=1,
        is_player1_turn=True,
        game_board=board,
        player1=create_test_player(is_player_1=True),
        player2=create_test_player(is_player_1=False),
    )


def create_empty_board() -> GameBoard:
    """Creates an empty game board with all idle cells."""
    board = [
        [
            Cell.get_default_idle_cell(row_index=i, col_index=j)
            for j in range(BOARD_SIZE)
        ]
        for i in range(BOARD_SIZE)
    ]
    return GameBoard(board, is_transient=False)


def create_test_player(is_player_1: bool) -> Player:
    """Creates a test player with default resources."""
    return Player(
        player_id=f"player-{'1' if is_player_1 else '2'}",
        individual_room_id=f"room-{'1' if is_player_1 else '2'}",
        user_id=f"user-{'1' if is_player_1 else '2'}",
        is_player_1=is_player_1,
        is_ai=not is_player_1,  # Player 2 is AI by default
        resources=PlayerResources.get_initial(),
        match_data=PlayerMatchData.get_initial(),
    )


def spawn_cell(board: GameBoard, row: int, col: int, owner: CellOwner) -> Cell:
    """
    Spawns a cell at the given position for the specified owner.

    Returns the spawned cell for further modification.
    """
    cell = board.get(row, col)

    if owner == CellOwner.PLAYER_1:
        cell.set_owned_by_player1()
    elif owner == CellOwner.PLAYER_2:
        cell.set_owned_by_player2()

    # Remove freshly spawned state so cell can act immediately
    cell.state = cell.state.remove_state(CellState.FRESHLY_SPAWNED)

    return cell
