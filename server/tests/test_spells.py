from constants.game_constants import SPELLS_MANA_COST
from game_engine.models.spells.spell_factory import get_initial_spell_deck, get_spell
from game_engine.models.spells.spell_id import SpellId


def test_all_spells_have_a_mana_cost():
    """
    Test that all spells have a mana cost defined in the SPELLS_MANA_COST dictionary.
    """

    missing_spells = [
        spell_id.name for spell_id in SpellId if spell_id not in SPELLS_MANA_COST
    ]
    assert (
        not missing_spells
    ), f"The following spells do not have a mana cost defined: {', '.join(missing_spells)}"


def test_all_spells_are_instanciable():
    """
    Test that all spells in SpellId can be instantiated using the get_spell function.
    """

    uninstanciable_spells = []
    for spell_id in SpellId:
        try:
            get_spell(spell_id)
        except KeyError:
            uninstanciable_spells.append(spell_id.name)

    assert (
        not uninstanciable_spells
    ), f"The following spells could not be instantiated: {', '.join(uninstanciable_spells)}"


def test_all_spells_are_present_in_the_player_deck():
    """
    Test that all spells in SpellId are present in the player's deck.
    """

    player_deck = get_initial_spell_deck()
    missing_spells = [
        spell_id.name for spell_id in SpellId if spell_id not in player_deck
    ]

    assert (
        not missing_spells
    ), f"The following spells are missing from the player's deck: {', '.join(missing_spells)}"
