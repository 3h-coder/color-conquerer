from typing import TYPE_CHECKING, Optional, List

from ai.strategy.decision_makers.base_decider import BaseDecider
from ai.strategy.scored_action import ScoredAction
from game_engine.models.actions.spell_casting import SpellCasting
from game_engine.models.spells.spell_factory import get_spell
from game_engine.models.spells.spell_id import SpellId
from utils.perf_utils import with_performance_logging
from ai.strategy.evaluators.spells import (
    AmbushEvaluator,
    MineTrapEvaluator,
    CelerityEvaluator,
    ArcheryVowEvaluator,
    ShieldFormationEvaluator,
)
from ai.config.ai_config import SpellWeights

if TYPE_CHECKING:
    from handlers.match_handler_unit import MatchHandlerUnit
    from ai.strategy.evaluators.board.board_evaluation import BoardEvaluation
    from ai.strategy.evaluators.spells.base_spell_evaluator import BaseSpellEvaluator


class SpellDecider(BaseDecider):
    """
    Decision maker for spell casting.
    Determines if a spell should be cast and which one.
    """

    STAMINA_THRESHOLD = 3

    # Spell evaluator registry - maps each spell to its evaluator class
    SPELL_EVALUATOR_REGISTRY: dict[SpellId, type["BaseSpellEvaluator"]] = {
        SpellId.AMBUSH: AmbushEvaluator,
        SpellId.MINE_TRAP: MineTrapEvaluator,
        SpellId.CELERITY: CelerityEvaluator,
        SpellId.ARCHERY_VOW: ArcheryVowEvaluator,
        SpellId.SHIELD_FORMATION: ShieldFormationEvaluator,
    }

    def __init__(self, match: "MatchHandlerUnit", ai_is_player1: bool):
        super().__init__(match, ai_is_player1)

        # Initialize evaluators for all registered spells
        self._evaluators: dict[SpellId, "BaseSpellEvaluator"] = {
            spell_id: evaluator_class(match, ai_is_player1)
            for spell_id, evaluator_class in self.SPELL_EVALUATOR_REGISTRY.items()
        }

    @with_performance_logging
    def decide_spell(
        self,
        board_evaluation: "BoardEvaluation",
    ) -> Optional[ScoredAction]:
        """
        Decides whether to cast a spell and returns the best ScoredAction if so.
        """
        player = (
            self._match_context.player1
            if self._ai_is_player1
            else self._match_context.player2
        )

        # 1. Check if we have any spells left
        available_spells = [
            spell_id for spell_id, count in player.resources.spells.items() if count > 0
        ]
        if not available_spells:
            return None

        # 2. Get all possible spell actions we can afford
        possible_actions: List[SpellCasting] = []
        transient_board = self._get_transient_board()

        for spell_id in available_spells:
            spell = get_spell(spell_id)
            if player.resources.current_mp >= spell.MANA_COST:
                spell_actions = SpellCasting.calculate(
                    spell, self._ai_is_player1, transient_board
                )
                possible_actions.extend(list(spell_actions))

        if not possible_actions:
            return None

        # 3. Decision Logic (Simple)

        # Priority A: Low Stamina - Cast regular spells to restore stamina
        if board_evaluation.ai_stamina < self.STAMINA_THRESHOLD:
            # We assign a huge artificial score to any spell when stamina is low
            # but still use _pick_best_action to get the most "useful" one among them
            return self._pick_best_action(
                possible_actions,
                lambda action: self._score_spell_action(action, board_evaluation)
                + SpellWeights.STAMINA_RECOVERY,
            )

        # Priority B: Strategic usage
        # We'll use a scoring system for simple strategic selection
        return self._pick_best_action(
            possible_actions,
            lambda action: self._score_spell_action(action, board_evaluation),
        )

    def _score_spell_action(
        self, action: SpellCasting, board_evaluation: "BoardEvaluation"
    ) -> float:
        """
        Scores a spell action by delegating to the appropriate evaluator.
        """
        score = 0.0
        spell_id = action.spell.ID

        # 1. General bonus for casting spells when we have plenty of mana
        if board_evaluation.ai_mp >= SpellWeights.MP_CONSERVATION_THRESHOLD:
            score += SpellWeights.MP_CONSERVATION_BONUS

        # 2. Delegate to spell-specific evaluator
        evaluator = self._evaluators.get(spell_id)
        if evaluator:
            score += evaluator.evaluate_spell(action, board_evaluation)

        return score
