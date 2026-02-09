import pytest
from unittest.mock import MagicMock
from game_engine.models.spells.spell_id import SpellId
from game_engine.models.actions.spell_casting import SpellCasting
from ai.strategy.evaluators.spells.ambush_evaluator import AmbushEvaluator
from ai.strategy.evaluators.spells.mine_trap_evaluator import MineTrapEvaluator
from ai.strategy.evaluators.spells.celerity_evaluator import CelerityEvaluator
from ai.strategy.evaluators.spells.archery_vow_evaluator import ArcheryVowEvaluator
from ai.strategy.evaluators.spells.shield_formation_evaluator import (
    ShieldFormationEvaluator,
)
from ai.config.ai_config import SpellWeights
from constants.game_constants import (
    PLAYER_1_ROWS,
    PLAYER_2_ROWS,
)
from game_engine.models.dtos.coordinates import Coordinates
from game_engine.models.cell.cell_owner import CellOwner


@pytest.fixture
def mock_spell_action():
    action = MagicMock(spec=SpellCasting)
    action.metadata = MagicMock()
    action.spell = MagicMock()
    return action


class TestSpellEvaluators:

    def test_ambush_evaluator_side_bonus(
        self, mock_match, board_evaluation, mock_spell_action
    ):
        evaluator = AmbushEvaluator(mock_match, ai_is_player1=True)
        mock_spell_action.spell.ID = SpellId.AMBUSH
        board_evaluation.current_turn = 1  # Ensure early game for side bonus logic

        # Target on P2 side (opponent side for P1)
        mock_spell_action.metadata.impacted_coords = Coordinates(PLAYER_2_ROWS[0], 5)
        score_opponent_side = evaluator.evaluate_spell(
            mock_spell_action, board_evaluation
        )

        # Target on P1 side
        mock_spell_action.metadata.impacted_coords = Coordinates(PLAYER_1_ROWS[0], 5)
        score_own_side = evaluator.evaluate_spell(mock_spell_action, board_evaluation)

        assert score_opponent_side > score_own_side
        # The difference includes both the opponent side bonus AND the distance to master factor difference
        # So we just check that it increased significantly
        assert (
            score_opponent_side - score_own_side
        ) >= SpellWeights.AMBUSH_EXTRA_SPAWN_BONUS

    def test_mine_trap_evaluator_cluster_bonus(
        self, mock_match, board_evaluation, mock_spell_action
    ):
        evaluator = MineTrapEvaluator(mock_match, ai_is_player1=True)
        mock_spell_action.spell.ID = SpellId.MINE_TRAP
        target_coords = Coordinates(5, 5)
        mock_spell_action.metadata.impacted_coords = target_coords

        # Mock board and neighbors
        mock_match.game_board.board = [
            [MagicMock() for _ in range(11)] for _ in range(11)
        ]
        for r in range(11):
            for c in range(11):
                mock_match.game_board.board[r][c].owner = CellOwner.NONE

        # Add an enemy cell next to target
        enemy_cell = mock_match.game_board.board[6][5]
        enemy_cell.owner = CellOwner.PLAYER_2

        # Case 1: No cluster
        board_evaluation.enemy_cell_clusters = []
        score_no_cluster = evaluator.evaluate_spell(mock_spell_action, board_evaluation)

        # Case 2: Large cluster containing the enemy neighbor
        board_evaluation.enemy_cell_clusters = [[enemy_cell, MagicMock(), MagicMock()]]
        score_cluster = evaluator.evaluate_spell(mock_spell_action, board_evaluation)

        assert score_cluster > score_no_cluster
        assert score_cluster - score_no_cluster == pytest.approx(
            SpellWeights.MINE_TRAP_ENEMY_CLUSTER_BONUS
        )

    def test_celerity_evaluator_advantage_bonus(
        self, mock_match, board_evaluation, mock_spell_action
    ):
        evaluator = CelerityEvaluator(mock_match, ai_is_player1=True)

        # Positive advantage
        board_evaluation.positional_advantage = 10.0
        score_adv = evaluator.evaluate_spell(mock_spell_action, board_evaluation)

        # Negative advantage
        board_evaluation.positional_advantage = -10.0
        score_disadv = evaluator.evaluate_spell(mock_spell_action, board_evaluation)

        assert score_adv > score_disadv
        assert score_adv - score_disadv == pytest.approx(
            SpellWeights.CELERITY_ADVANTAGE_BONUS
        )

    def test_archery_vow_evaluator_forward_bonus(
        self, mock_match, board_evaluation, mock_spell_action
    ):
        evaluator = ArcheryVowEvaluator(mock_match, ai_is_player1=True)

        # Forward position (closer to enemy master at 9,5)
        mock_spell_action.metadata.impacted_coords = Coordinates(8, 5)
        score_forward = evaluator.evaluate_spell(mock_spell_action, board_evaluation)

        # Backward position
        mock_spell_action.metadata.impacted_coords = Coordinates(1, 5)
        score_backward = evaluator.evaluate_spell(mock_spell_action, board_evaluation)

        assert score_forward > score_backward

    def test_shield_formation_evaluator_critical_bonus(
        self, mock_match, board_evaluation, mock_spell_action
    ):
        evaluator = ShieldFormationEvaluator(mock_match, ai_is_player1=True)

        # Normal state
        board_evaluation.ai_master_in_critical_danger.return_value = False
        board_evaluation.ai_is_losing.return_value = False
        score_normal = evaluator.evaluate_spell(mock_spell_action, board_evaluation)

        # Critical state
        board_evaluation.ai_master_in_critical_danger.return_value = True
        score_critical = evaluator.evaluate_spell(mock_spell_action, board_evaluation)

        assert score_critical > score_normal
        assert score_critical - score_normal == pytest.approx(
            SpellWeights.SHIELD_FORMATION_CRITICAL_BONUS
        )
