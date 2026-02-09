from typing import TYPE_CHECKING
from ai.strategy.evaluators.spells.base_spell_evaluator import BaseSpellEvaluator
from game_engine.models.dtos.coordinates import Coordinates
from utils.board_utils import get_diagonal_formations
from ai.config.ai_config import SpellWeights

if TYPE_CHECKING:
    from game_engine.models.actions.spell_casting import SpellCasting
    from ai.strategy.evaluators.board.board_evaluation import BoardEvaluation


class CelerityEvaluator(BaseSpellEvaluator):
    # Turn thresholds for game-phase awareness
    EARLY_GAME_TURN_THRESHOLD = 5  # Before this turn, cells aren't in combat range yet

    def evaluate_spell(
        self, action: "SpellCasting", board_evaluation: "BoardEvaluation"
    ) -> float:
        # Early game penalty: cells aren't in combat range for double-action to matter
        if board_evaluation.current_turn < self.EARLY_GAME_TURN_THRESHOLD:
            return 2.0  # Very low score - prefer spawning instead

        score = SpellWeights.CELERITY_BASE
        # Bonus if we are already in a good position to press the advantage
        if board_evaluation.positional_advantage > 0:
            score += SpellWeights.CELERITY_ADVANTAGE_BONUS

        # Analyze the diagonal formation this target belongs to
        target_coords = action.metadata.impacted_coords
        diagonal_cells = self._get_diagonal_formation(target_coords)

        # Bonus based on diagonal size (more cells = more value)
        score += len(diagonal_cells) * SpellWeights.CELERITY_PER_CELL_BONUS

        # Bonus for special cells in the diagonal (archers, master, shielded)
        special_cell_count = self._count_special_cells(diagonal_cells)
        score += special_cell_count * SpellWeights.CELERITY_SPECIAL_CELL_BONUS

        # Penalty for already-accelerated cells (avoid redundancy)
        accelerated_count = self._count_accelerated_cells(diagonal_cells)
        score -= accelerated_count * SpellWeights.CELERITY_REDUNDANT_PENALTY

        return score

    def _get_diagonal_formation(self, start_coords: Coordinates) -> list[Coordinates]:
        """Find the diagonal formation that the target cell belongs to."""
        board = self._match_context.game_board
        ai_cells = board.get_cells_owned_by_player(player1=self._ai_is_player1)

        # Build set of AI cell coordinates for fast lookup
        ai_coords_set = {(cell.row_index, cell.column_index) for cell in ai_cells}

        # Use shared utility to get both diagonals
        diagonal1, diagonal2 = get_diagonal_formations(
            start_coords.row_index, start_coords.column_index, ai_coords_set
        )

        # Convert tuples back to Coordinates and return the longer diagonal
        if len(diagonal1) >= len(diagonal2):
            return (
                [Coordinates(r, c) for r, c in diagonal1]
                if diagonal1
                else [start_coords]
            )
        else:
            return (
                [Coordinates(r, c) for r, c in diagonal2]
                if diagonal2
                else [start_coords]
            )

    def _count_special_cells(self, diagonal_cells: list[Coordinates]) -> int:
        """Count special cells (archer, master, shielded) in the diagonal."""
        board = self._match_context.game_board
        count = 0

        for coords in diagonal_cells:
            cell = board.get(coords.row_index, coords.column_index)
            if cell.is_archer() or cell.is_master or cell.is_shielded():
                count += 1

        return count

    def _count_accelerated_cells(self, diagonal_cells: list[Coordinates]) -> int:
        """Count already-accelerated cells in the diagonal."""
        board = self._match_context.game_board
        count = 0

        for coords in diagonal_cells:
            cell = board.get(coords.row_index, coords.column_index)
            if cell.is_accelerated():
                count += 1

        return count
