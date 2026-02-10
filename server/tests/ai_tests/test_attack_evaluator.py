import pytest
from unittest.mock import MagicMock
from ai.strategy.evaluators.attack_evaluator import AttackEvaluator
from ai.config.ai_config import AttackWeights
from game_engine.models.dtos.coordinates import Coordinates
from game_engine.models.cell.cell import Cell


class TestAttackEvaluator:
    """Tests for AttackEvaluator."""

    def test_evaluate_enemy_master(
        self, attack_evaluator: AttackEvaluator, board_evaluation: MagicMock
    ) -> None:
        """Test that attacking the enemy master is highly prioritized."""
        # Arrange
        # Enemy master at (9, 5) - defined in conftest.py
        coords = Coordinates(9, 5)
        board_evaluation.ai_has_lethal_opportunity.return_value = False

        # Act
        score = attack_evaluator.evaluate(coords, board_evaluation)

        # Assert
        assert score == AttackWeights.ENEMY_MASTER

    def test_evaluate_lethal_master(
        self, attack_evaluator: AttackEvaluator, board_evaluation: MagicMock
    ) -> None:
        """Test that lethal opportunities on enemy master get a major bonus."""
        # Arrange
        # Enemy master at (9, 5)
        coords = Coordinates(9, 5)
        board_evaluation.ai_has_lethal_opportunity.return_value = True

        # Act
        score = attack_evaluator.evaluate(coords, board_evaluation)

        # Assert
        assert score == AttackWeights.ENEMY_MASTER + AttackWeights.LETHAL_ON_MASTER

    def test_evaluate_basic_unit(
        self, attack_evaluator: AttackEvaluator, board_evaluation: MagicMock
    ) -> None:
        """Test basic attack scoring for regular units."""
        # Arrange
        coords = Coordinates(5, 5)
        board_evaluation.enemy_cells_near_ai_master = []

        target_cell = MagicMock(spec=Cell)
        target_cell.is_shielded.return_value = True
        target_cell.is_archer.return_value = False

        attack_evaluator._match_context.game_board = MagicMock()
        attack_evaluator._match_context.game_board.get.return_value = target_cell

        # Act
        score = attack_evaluator.evaluate(coords, board_evaluation)

        # Assert
        assert score == AttackWeights.BASE_ATTACK

    def test_evaluate_threat_defensive(
        self, attack_evaluator: AttackEvaluator, board_evaluation: MagicMock
    ) -> None:
        """Test that targets near our own master are prioritized."""
        # Arrange
        coords = Coordinates(2, 5)
        target_cell = MagicMock(spec=Cell)
        target_cell.is_shielded.return_value = True
        target_cell.is_archer.return_value = False

        board_evaluation.enemy_cells_near_ai_master = [target_cell]
        attack_evaluator._match_context.game_board = MagicMock()
        attack_evaluator._match_context.game_board.get.return_value = target_cell

        # Act
        score = attack_evaluator.evaluate(coords, board_evaluation)

        # Assert
        assert score == AttackWeights.BASE_ATTACK + AttackWeights.THREAT_DEFENSE

    def test_evaluate_low_hp_clear(
        self, attack_evaluator: AttackEvaluator, board_evaluation: MagicMock
    ) -> None:
        """Test that non-shielded targets get a bonus (easier to clear)."""
        # Arrange
        coords = Coordinates(5, 5)
        target_cell = MagicMock(spec=Cell)
        target_cell.is_shielded.return_value = False
        target_cell.is_archer.return_value = False
        board_evaluation.enemy_cells_near_ai_master = []

        attack_evaluator._match_context.game_board = MagicMock()
        attack_evaluator._match_context.game_board.get.return_value = target_cell

        # Act
        score = attack_evaluator.evaluate(coords, board_evaluation)

        # Assert
        assert score == AttackWeights.BASE_ATTACK + AttackWeights.LOW_HP_BONUS

    def test_master_at_critical_health_refuses_non_lethal_attacks(
        self, attack_evaluator: AttackEvaluator, board_evaluation: MagicMock
    ) -> None:
        """Test that master with critical health refuses to attack non-master targets."""
        # Arrange
        coords = Coordinates(5, 5)
        target_cell = MagicMock(spec=Cell)
        target_cell.is_shielded.return_value = False
        target_cell.is_archer.return_value = False

        # Set master health to critical (2 HP)
        attack_evaluator._match_context.player1.resources.current_hp = 2

        # Master position (attacker coords)
        master_coords = Coordinates(0, 5)
        master_cell = MagicMock(spec=Cell)
        master_cell.is_master = True

        board_evaluation.enemy_cells_near_ai_master = []
        attack_evaluator._match_context.game_board = MagicMock()

        def get_cell(row, col):
            if row == 0 and col == 5:  # Master position
                return master_cell
            return target_cell

        attack_evaluator._match_context.game_board.get.side_effect = get_cell

        # Act
        score = attack_evaluator.evaluate(
            coords, board_evaluation, attacker_coords=master_coords
        )

        # Assert
        assert score == 0.0  # Master refuses to attack when health is critical

    def test_master_at_critical_health_attacks_enemy_master_if_lethal(
        self, attack_evaluator: AttackEvaluator, board_evaluation: MagicMock
    ) -> None:
        """Test that master with critical health CAN attack enemy master if it leads to victory."""
        # Arrange
        enemy_master_coords = Coordinates(9, 5)

        # Set master health to critical (2 HP)
        attack_evaluator._match_context.player1.resources.current_hp = 2

        # Master position (attacker coords)
        master_coords = Coordinates(0, 5)
        master_cell = MagicMock(spec=Cell)
        master_cell.is_master = True

        board_evaluation.enemy_master_coords = enemy_master_coords
        board_evaluation.ai_has_lethal_opportunity.return_value = True

        attack_evaluator._match_context.game_board = MagicMock()
        attack_evaluator._match_context.game_board.get.return_value = master_cell

        # Act
        score = attack_evaluator.evaluate(
            enemy_master_coords, board_evaluation, attacker_coords=master_coords
        )

        # Assert
        assert score == AttackWeights.ENEMY_MASTER + AttackWeights.LETHAL_ON_MASTER

    def test_master_at_critical_health_refuses_non_lethal_master_attack(
        self, attack_evaluator: AttackEvaluator, board_evaluation: MagicMock
    ) -> None:
        """Test that master with critical health refuses to attack enemy master without lethal."""
        # Arrange
        enemy_master_coords = Coordinates(9, 5)

        # Set master health to critical (2 HP)
        attack_evaluator._match_context.player1.resources.current_hp = 2

        # Master position (attacker coords)
        master_coords = Coordinates(0, 5)
        master_cell = MagicMock(spec=Cell)
        master_cell.is_master = True

        board_evaluation.enemy_master_coords = enemy_master_coords
        board_evaluation.ai_has_lethal_opportunity.return_value = False  # NOT lethal!

        attack_evaluator._match_context.game_board = MagicMock()
        attack_evaluator._match_context.game_board.get.return_value = master_cell

        # Act
        score = attack_evaluator.evaluate(
            enemy_master_coords, board_evaluation, attacker_coords=master_coords
        )

        # Assert
        assert score == 0.0  # Master refuses - too risky!

    def test_evaluate_archer_elimination(
        self, attack_evaluator: AttackEvaluator, board_evaluation: MagicMock
    ) -> None:
        """Test that targeting an enemy archer gets a bonus."""
        # Arrange
        coords = Coordinates(5, 5)
        target_cell = MagicMock(spec=Cell)
        target_cell.is_shielded.return_value = True
        target_cell.is_archer.return_value = True
        board_evaluation.enemy_cells_near_ai_master = []

        attack_evaluator._match_context.game_board = MagicMock()
        attack_evaluator._match_context.game_board.get.return_value = target_cell

        # Act
        score = attack_evaluator.evaluate(coords, board_evaluation)

        # Assert
        assert score == AttackWeights.BASE_ATTACK + AttackWeights.ARCHER_TARGET_BONUS

    def test_evaluate_master_retaliation_penalty(
        self, attack_evaluator: AttackEvaluator, board_evaluation: MagicMock
    ) -> None:
        """Test that master's attack on non-master units is penalized."""
        # Arrange
        coords = Coordinates(5, 5)
        target_cell = MagicMock(spec=Cell)
        target_cell.is_shielded.return_value = True
        target_cell.is_archer.return_value = False
        board_evaluation.enemy_cells_near_ai_master = []

        # Attacker is master
        master_coords = Coordinates(0, 0)
        master_cell = MagicMock(spec=Cell)
        master_cell.is_master = True

        attack_evaluator._match_context.game_board = MagicMock()

        def get_cell(row, col):
            if row == 0 and col == 0:
                return master_cell
            return target_cell

        attack_evaluator._match_context.game_board.get.side_effect = get_cell

        # Act
        score = attack_evaluator.evaluate(
            coords, board_evaluation, attacker_coords=master_coords
        )

        # Assert
        assert (
            score
            == AttackWeights.BASE_ATTACK + AttackWeights.MASTER_RETALIATION_PENALTY
        )

    def test_evaluate_critical_threat_defense(
        self, attack_evaluator: AttackEvaluator, board_evaluation: MagicMock
    ) -> None:
        """Test that threat defense is significantly boosted when master is critical."""
        # Arrange
        target_coords = Coordinates(2, 5)
        target_cell = MagicMock(spec=Cell)
        target_cell.is_shielded.return_value = True
        target_cell.is_archer.return_value = False

        # Target cell is near master
        board_evaluation.enemy_cells_near_ai_master = [target_cell]

        # Master is critical (but not suicidal)
        attack_evaluator._match_context.player1.resources.current_hp = 2

        attack_evaluator._match_context.game_board = MagicMock()
        attack_evaluator._match_context.game_board.get.return_value = target_cell

        # Act
        score = attack_evaluator.evaluate(target_coords, board_evaluation)

        # Assert
        expected_score = (
            AttackWeights.BASE_ATTACK
            + AttackWeights.THREAT_DEFENSE
            + AttackWeights.CRITICAL_THREAT_DEFENSE
        )
        assert score == expected_score
