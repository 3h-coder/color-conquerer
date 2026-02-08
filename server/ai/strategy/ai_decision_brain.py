from typing import TYPE_CHECKING, Optional, Any
from ai.strategy.evaluators.board.board_evaluator import BoardEvaluator
from ai.strategy.decision_makers.spawn_decider import SpawnDecider
from ai.strategy.decision_makers.attack_decider import AttackDecider
from ai.strategy.decision_makers.movement_decider import MovementDecider

if TYPE_CHECKING:
    from handlers.match_handler_unit import MatchHandlerUnit
    from ai.strategy.evaluators.board.board_evaluation import BoardEvaluation


class AIDecisionBrain:
    """
    Brain component of the AI that selects the best next action.
    """

    def __init__(self, match: "MatchHandlerUnit", ai_is_player1: bool):
        self._match = match
        self._ai_is_player1 = ai_is_player1

        # Initialize evaluators and deciders
        self._board_evaluator = BoardEvaluator(match, ai_is_player1)
        self._spawn_decider = SpawnDecider(match, ai_is_player1)
        self._attack_decider = AttackDecider(match, ai_is_player1)
        self._movement_decider = MovementDecider(match, ai_is_player1)

    def decide_next_best_action(self) -> Optional[Any]:
        """
        Observes the current board state and decides on the best next action.
        This is the main entry point for the AI's "thinking" phase.
        """
        evaluation = self._evaluate_board()
        return self._decide_action(evaluation)

    def _evaluate_board(self) -> "BoardEvaluation":
        """Returns a fresh evaluation of the board."""
        return self._board_evaluator.evaluate()

    def _decide_action(self, evaluation: "BoardEvaluation") -> Optional[Any]:
        """
        Decision engine: checks deciders in priority order.
        Returns the action object to be executed, or None if no actions are taken.
        """
        # 1. Movement (Advancing position)
        movement_action = self._movement_decider.decide_movement(evaluation)
        if movement_action:
            return movement_action

        # 2. Attacks (Critical Defense & Offensive)
        attack_action = self._attack_decider.decide_attack(evaluation)
        if attack_action:
            return attack_action

        # 3. Spawning (Strategic placement)
        spawn_action = self._spawn_decider.decide_spawn(evaluation)
        if spawn_action:
            return spawn_action

        # 4. Spells (TODO)

        return None
