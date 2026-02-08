from typing import TYPE_CHECKING, Optional
from game_engine.models.actions.cell_spawn import CellSpawn
from ai.strategy.evaluators.spawn_evaluator import SpawnEvaluator
from game_engine.action_calculation import get_possible_spawns
from utils.perf_utils import with_performance_logging
from ai.strategy.decision_makers.base_decider import BaseDecider

if TYPE_CHECKING:
    from handlers.match_handler_unit import MatchHandlerUnit
    from ai.strategy.evaluators.board.board_evaluation import BoardEvaluation


class SpawnDecider(BaseDecider):
    """
    Decision maker for cell spawning.
    Determines if a cell should be spawned and where.
    """

    def __init__(self, match: "MatchHandlerUnit", ai_is_player1: bool):
        super().__init__(match, ai_is_player1)
        self._evaluator = SpawnEvaluator(match, ai_is_player1)

    @with_performance_logging
    def decide_spawn(
        self,
        board_evaluation: "BoardEvaluation",
    ) -> Optional[CellSpawn]:
        """
        Decides whether to spawn a cell and returns the best CellSpawn action if so.
        """
        player = (
            self._match_context.player1
            if self._ai_is_player1
            else self._match_context.player2
        )

        # 1. Check if AI has enough mana
        if player.resources.current_mp < CellSpawn.DEFAULT_MANA_COST:
            return None

        # 2. Get all possible spawns.
        transient_board = self._get_transient_board()
        possible_spawns = get_possible_spawns(self._ai_is_player1, transient_board)
        if not possible_spawns:
            return None

        # 3. Evaluate each location and pick the best one
        return self._pick_best_action(
            possible_spawns,
            lambda spawn: self._evaluator.evaluate(
                spawn.metadata.impacted_coords, board_evaluation
            ),
        )
