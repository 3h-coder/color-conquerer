from typing import TYPE_CHECKING, Optional, Any
from ai.strategy.evaluators.board.board_evaluator import BoardEvaluator
from ai.strategy.decision_makers.spawn_decider import SpawnDecider
from ai.strategy.decision_makers.attack_decider import AttackDecider
from ai.strategy.decision_makers.movement_decider import MovementDecider
from ai.strategy.decision_makers.spell_decider import SpellDecider
from ai.strategy.scored_action import ScoredAction
from game_engine.models.actions.cell_attack import CellAttack
from config.logging import get_configured_logger
from ai.config.ai_config import (
    MASTER_SUICIDAL_HEALTH_THRESHOLD,
    MASTER_CRITICAL_HEALTH_THRESHOLD,
)

if TYPE_CHECKING:
    from handlers.match_handler_unit import MatchHandlerUnit
    from ai.strategy.evaluators.board.board_evaluation import BoardEvaluation


class AIDecisionBrain:
    """
    Brain component of the AI that selects the best next action.
    """

    def __init__(self, match: "MatchHandlerUnit", ai_is_player1: bool):
        self._logger = get_configured_logger(__name__)
        self._match = match
        self._ai_is_player1 = ai_is_player1

        # Initialize evaluators and deciders
        self._board_evaluator = BoardEvaluator(match, ai_is_player1)
        self._spawn_decider = SpawnDecider(match, ai_is_player1)
        self._attack_decider = AttackDecider(match, ai_is_player1)
        self._movement_decider = MovementDecider(match, ai_is_player1)
        self._spell_decider = SpellDecider(match, ai_is_player1)

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
        Unified decision engine: all deciders compete on the same scoring scale.
        Each decider returns a ScoredAction (action + score) and the highest score wins.
        Returns the action object to be executed, or None if no actions are available.

        Filters out suicidal actions (master at critical health attacking non-lethally)
        unless doing so would result in a draw (both masters at critical health).
        """
        candidates: list[ScoredAction] = []

        movement = self._movement_decider.decide_movement(evaluation)
        if movement:
            candidates.append(movement)

        attack = self._attack_decider.decide_attack(evaluation)
        if attack:
            candidates.append(attack)

        spell = self._spell_decider.decide_spell(evaluation)
        if spell:
            candidates.append(spell)

        spawn = self._spawn_decider.decide_spawn(evaluation)
        if spawn:
            candidates.append(spawn)

        if not candidates:
            return None

        # Filter out suicidal actions (master attacking when at critical health without lethal)
        safe_candidates = [c for c in candidates if not self._is_suicidal_action(c)]

        # If all candidates are suicidal, only allow if it's a draw scenario
        if not safe_candidates:
            # Check if this is a draw scenario (both masters at critical health)
            if self._is_draw_scenario():
                safe_candidates = candidates
            else:
                self._logger.warning(
                    "All actions are suicidal and not a draw scenario. No action taken."
                )
                return None

        self._logger.info("All candidate actions: %s", safe_candidates)
        best = max(safe_candidates, key=lambda c: c.score)
        self._logger.info(
            "Selected best action: %s with score %s", best.action, best.score
        )
        return best.action

    def _is_suicidal_action(self, scored_action: ScoredAction) -> bool:
        """
        Checks if an action would result in the master dying.
        A suicidal action is one where our master has suicidal health (would die from any damage).
        Returns True if the action should be avoided (is suicidal).
        """
        action = scored_action.action

        # Only attacks can be suicidal
        if not isinstance(action, CellAttack):
            return False

        # Suicidal = master has reached suicidal health threshold (would die from any damage)
        ai_player = (
            self._match.match_context.player1
            if self._ai_is_player1
            else self._match.match_context.player2
        )
        return ai_player.resources.current_hp == MASTER_SUICIDAL_HEALTH_THRESHOLD

    def _is_draw_scenario(self) -> bool:
        """
        Checks if this is a draw scenario where both masters are at critical health
        and the AI attacking would result in mutual destruction.
        """
        ai_player = (
            self._match.match_context.player1
            if self._ai_is_player1
            else self._match.match_context.player2
        )
        enemy_player = (
            self._match.match_context.player2
            if self._ai_is_player1
            else self._match.match_context.player1
        )

        # Both masters at critical health = draw scenario
        return (
            ai_player.resources.current_hp == 1
            and enemy_player.resources.current_hp == 1
        )
