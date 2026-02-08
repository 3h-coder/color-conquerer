import pytest
from unittest.mock import MagicMock, patch
from ai.strategy.decision_makers.spell_decider import SpellDecider
from game_engine.models.spells.spell_id import SpellId
from game_engine.models.actions.spell_casting import SpellCasting
from game_engine.models.dtos.coordinates import Coordinates
from ai.config.ai_config import SPELL_WEIGHT_STAMINA_RECOVERY


class TestSpellDecider:

    @patch("ai.strategy.decision_makers.spell_decider.get_spell")
    @patch("ai.strategy.decision_makers.spell_decider.SpellCasting.calculate")
    def test_decide_spell_prioritizes_stamina_when_low(
        self, mock_calculate, mock_get_spell, mock_match, board_evaluation
    ):
        # Arrange
        ai_is_player1 = True
        decider = SpellDecider(mock_match, ai_is_player1)

        # Mock player with spells and mana
        player = mock_match.match_context.player1
        player.resources.spells = {SpellId.MINE_TRAP: 1}
        player.resources.current_mp = 10

        # Mock spell and available action
        mock_spell = MagicMock()
        mock_spell.ID = SpellId.MINE_TRAP
        mock_spell.MANA_COST = 1
        mock_get_spell.return_value = mock_spell

        mock_action = MagicMock(spec=SpellCasting)
        mock_action.spell = mock_spell
        mock_action.metadata = MagicMock()
        mock_action.metadata.impacted_coords = Coordinates(5, 5)
        mock_calculate.return_value = [mock_action]

        # Low stamina
        board_evaluation.ai_stamina = 1
        decider.STAMINA_THRESHOLD = 3

        # Act
        action = decider.decide_spell(board_evaluation)

        # Assert
        assert action == mock_action

    def test_decide_spell_returns_none_if_no_mana(self, mock_match, board_evaluation):
        # Arrange
        ai_is_player1 = True
        decider = SpellDecider(mock_match, ai_is_player1)

        player = mock_match.match_context.player1
        player.resources.spells = {SpellId.MINE_TRAP: 1}
        player.resources.current_mp = 0  # No mana

        # Act
        action = decider.decide_spell(board_evaluation)

        # Assert
        assert action is None

    def test_decide_spell_returns_none_if_no_spells(self, mock_match, board_evaluation):
        # Arrange
        ai_is_player1 = True
        decider = SpellDecider(mock_match, ai_is_player1)

        player = mock_match.match_context.player1
        player.resources.spells = {SpellId.MINE_TRAP: 0}  # No charges left

        # Act
        action = decider.decide_spell(board_evaluation)

        # Assert
        assert action is None
