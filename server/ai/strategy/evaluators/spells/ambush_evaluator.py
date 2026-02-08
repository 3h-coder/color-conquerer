from typing import TYPE_CHECKING
from ai.strategy.evaluators.spells.base_spell_evaluator import BaseSpellEvaluator
from ai.config.ai_config import (
    SPELL_WEIGHT_AMBUSH_BASE,
    SPELL_WEIGHT_AMBUSH_EXTRA_SPAWN_BONUS,
    SPELL_WEIGHT_AMBUSH_ARCHER_TARGET_BONUS,
    SPELL_WEIGHT_AMBUSH_MASTER_TARGET_BONUS,
)

if TYPE_CHECKING:
    from game_engine.models.actions.spell_casting import SpellCasting
    from ai.strategy.evaluators.board.board_evaluation import BoardEvaluation


class AmbushEvaluator(BaseSpellEvaluator):
    EARLY_GAME_TURN_THRESHOLD = 6  # Before this turn, opponents on their side

    def evaluate_spell(
        self, action: "SpellCasting", board_evaluation: "BoardEvaluation"
    ) -> float:
        score = SPELL_WEIGHT_AMBUSH_BASE
        target_coords = action.metadata.impacted_coords
        board = self._match_context.game_board
        target_cell = board.get(target_coords.row_index, target_coords.column_index)
        is_early_game = board_evaluation.current_turn <= self.EARLY_GAME_TURN_THRESHOLD
        on_opponent_side = target_coords.is_on_player_side(
            of_player1=not self._ai_is_player1
        )

        # Ambush is only valuable in specific situations:

        # 1. Extra spawn from opponent's side positioning (early game)
        extra_spawn_available = is_early_game and on_opponent_side
        if extra_spawn_available:
            score += SPELL_WEIGHT_AMBUSH_EXTRA_SPAWN_BONUS

        # 2. Targeting an archer (high-priority threat)
        if target_cell.is_archer():
            score += SPELL_WEIGHT_AMBUSH_ARCHER_TARGET_BONUS

        # 3. Targeting enemy master with extra spawn available = massive pressure
        is_enemy_master = (
            target_coords.row_index == board_evaluation.enemy_master_coords.row_index
            and target_coords.column_index
            == board_evaluation.enemy_master_coords.column_index
        )
        if is_enemy_master and extra_spawn_available:
            score += SPELL_WEIGHT_AMBUSH_MASTER_TARGET_BONUS

        return score
