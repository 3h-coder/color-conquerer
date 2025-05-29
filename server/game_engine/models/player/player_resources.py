from dataclasses import dataclass

from constants.game_constants import MAX_HP_VALUE, MAX_MP_VALUE, MAX_STAMINA_VALUE
from dto.player.player_resources_dto import PlayerResourcesDto
from dto.spell.spell_dto import SpellDto
from dto.spell.spells_dto import SpellsDto
from game_engine.models.spells.spell_factory import get_initial_spell_deck, get_spell
from game_engine.models.spells.spell_id import SpellId


@dataclass
class PlayerResources:
    """
    The player resources that the player uses directly or indirectly during a match,
    such as HP, MP, stamina and their spells.
    """

    max_hp: int
    current_hp: int
    max_mp: int
    current_mp: int
    # Spell id | count
    spells: dict[SpellId, int]
    current_stamina: int
    max_stamina: int

    @staticmethod
    def get_initial():
        return PlayerResources(
            max_hp=MAX_HP_VALUE,
            current_hp=MAX_HP_VALUE,
            max_mp=MAX_MP_VALUE,
            current_mp=1,
            spells=get_initial_spell_deck(),
            current_stamina=MAX_STAMINA_VALUE,
            max_stamina=MAX_STAMINA_VALUE,
        )

    def to_dto(self):
        return PlayerResourcesDto(
            maxHP=self.max_hp,
            currentHP=self.current_hp,
            maxMP=self.max_mp,
            currentMP=self.current_mp,
            currentStamina=self.current_stamina,
            maxStamina=self.max_stamina,
        )

    def get_spells_dto(self):
        result: list[SpellDto] = []

        for spell_id in self.spells:
            count = self.spells[spell_id]
            spell = get_spell(spell_id)
            result.append(spell.to_dto(count))

        return SpellsDto(result)
