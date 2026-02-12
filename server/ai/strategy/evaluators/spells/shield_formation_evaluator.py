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

        # Retrieve the full formation this target coordinate belongs to
        target_coords = action.metadata.impacted_coords
        square_cells = action.spell.get_impacted_cells(target_coords)

        # Calculate counts of AI-owned shielded vs non-shielded cells
        shielded_count, non_shielded_count = self._get_shield_stats(square_cells)

        # Apply bonus for non-shielded and penalty for already-shielded
        score += non_shielded_count * SpellWeights.SHIELD_FORMATION_PER_CELL_BONUS
        score -= shielded_count * SpellWeights.SHIELD_FORMATION_REDUNDANT_PENALTY

        # Clamp score: must be non-negative and not exceed critical move threshold (lethal on master is 200)
        return max(0.0, min(190.0, score))

    def _get_shield_stats(self, square_cells: list[Coordinates]) -> tuple[int, int]:
        """Count already-shielded vs non-shielded friendly cells in the square."""
        board = self._match_context.game_board
        shielded = 0
        non_shielded = 0

        for coords in square_cells:
            cell = board.get(coords.row_index, coords.column_index)
            # Only consider cells that belong to the AI player
            if cell and cell.belongs_to(self._ai_is_player1):
                if cell.is_shielded():
                    shielded += 1
                else:
                    non_shielded += 1

        return shielded, non_shielded
