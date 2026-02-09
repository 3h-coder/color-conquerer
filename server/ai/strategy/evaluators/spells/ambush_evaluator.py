from typing import TYPE_CHECKING
from game_engine.models.dtos.coordinates import Coordinates
from ai.strategy.evaluators.spells.base_spell_evaluator import BaseSpellEvaluator
from ai.config.ai_config import SpellWeights

if TYPE_CHECKING:
    from game_engine.models.actions.spell_casting import SpellCasting
    from ai.strategy.evaluators.board.board_evaluation import BoardEvaluation
    from game_engine.models.cell.cell import Cell
    from game_engine.models.game_board import GameBoard


class AmbushEvaluator(BaseSpellEvaluator):
    EARLY_GAME_TURN_THRESHOLD = 6  # Before this turn, opponents on their side

    def evaluate_spell(
        self, action: "SpellCasting", board_evaluation: "BoardEvaluation"
    ) -> float:
        score = SpellWeights.AMBUSH_BASE
        target_coords = action.metadata.impacted_coords
        board = self._match_context.game_board
        target_cell = board.get(target_coords.row_index, target_coords.column_index)
        is_early_game = board_evaluation.current_turn <= self.EARLY_GAME_TURN_THRESHOLD
        on_opponent_side = target_coords.is_on_player_side(
            of_player1=not self._ai_is_player1
        )

        # Check if master is at critical health
        master_is_critical = self._is_ai_master_critical_health()

        # Ambush is only valuable in specific situations:

        # 1. Extra spawn from opponent's side positioning (early game)
        extra_spawn_available = is_early_game and on_opponent_side
        if extra_spawn_available:
            score += self._evaluate_extra_spawn_bonus()

        # 2. Targeting an archer (high-priority threat)
        score += self._evaluate_archer_threat_bonus(
            target_cell, master_is_critical, target_coords, board
        )

        # 3. Targeting enemy master with extra spawn available = massive pressure
        if (
            self._is_enemy_master(target_coords, board_evaluation)
            and extra_spawn_available
        ):
            score += SpellWeights.AMBUSH_MASTER_TARGET_BONUS

        return score

    def _evaluate_extra_spawn_bonus(self) -> float:
        """Bonus for ambushing on opponent's side in early game."""
        return SpellWeights.AMBUSH_EXTRA_SPAWN_BONUS

    def _evaluate_archer_threat_bonus(
        self,
        target_cell: "Cell",
        master_is_critical: bool,
        target_coords: Coordinates,
        board: "GameBoard",
    ) -> float:
        """
        Bonus for targeting an archer, but only if there are no friendly cells
        already positioned to handle it (no nearby friendly units).
        """
        if not target_cell.is_archer():
            return 0.0

        # Check if there are friendly cells already near this archer
        archer_neighbors = board.get_neighbours(
            target_coords.row_index, target_coords.column_index
        )
        friendly_neighbors = [
            n
            for n in archer_neighbors
            if n.is_owned() and n.belongs_to(self._ai_is_player1)
        ]

        # If we already have friendly cells nearby, don't need ambush
        if friendly_neighbors:
            return 0.0

        score = SpellWeights.AMBUSH_ARCHER_TARGET_BONUS
        # Boost further if master is critical - eliminate threats urgently
        if master_is_critical:
            score += SpellWeights.AMBUSH_CRITICAL_HEALTH_BONUS

        return score

    def _is_enemy_master(
        self, target_coords: Coordinates, board_evaluation: "BoardEvaluation"
    ) -> bool:
        """Check if target is the enemy master."""
        return (
            target_coords.row_index == board_evaluation.enemy_master_coords.row_index
            and target_coords.column_index
            == board_evaluation.enemy_master_coords.column_index
        )
