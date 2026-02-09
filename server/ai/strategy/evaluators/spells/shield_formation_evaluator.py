from typing import TYPE_CHECKING
from ai.strategy.evaluators.spells.base_spell_evaluator import BaseSpellEvaluator
from game_engine.models.dtos.coordinates import Coordinates
from ai.config.ai_config import SpellWeights

if TYPE_CHECKING:
    from game_engine.models.actions.spell_casting import SpellCasting
    from ai.strategy.evaluators.board.board_evaluation import BoardEvaluation


class ShieldFormationEvaluator(BaseSpellEvaluator):
    def evaluate_spell(
        self, action: "SpellCasting", board_evaluation: "BoardEvaluation"
    ) -> float:
        # Shield formation targets a square of any size (guaranteed by calculation logic)
        score = SpellWeights.SHIELD_FORMATION_BASE

        # Bonus if we are losing or AI master is under threat
        if (
            board_evaluation.ai_master_in_critical_danger()
            or board_evaluation.ai_is_losing()
        ):
            score += SpellWeights.SHIELD_FORMATION_CRITICAL_BONUS

        # Penalty for already-shielded cells (avoid redundancy)
        square_cells = action.metadata.impacted_coords
        shielded_count = self._count_shielded_cells(square_cells)
        score -= shielded_count * SpellWeights.SHIELD_FORMATION_REDUNDANT_PENALTY

        return score

    def _count_shielded_cells(self, square_cells: list[Coordinates]) -> int:
        """Count already-shielded friendly cells in the square."""
        board = self._match_context.game_board
        count = 0

        for coords in square_cells:
            cell = board.get(coords.row_index, coords.column_index)
            # Only count if cell exists, is shielded, AND belongs to the AI player
            if cell and cell.is_shielded() and cell.belongs_to(self._ai_is_player1):
                count += 1

        return count
