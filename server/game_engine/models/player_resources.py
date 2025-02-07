from dataclasses import dataclass

from constants.match_constants import MAX_HP_VALUE, MAX_MP_VALUE
from dto.player_resources_dto import PlayerResourcesDto
from game_engine.models.spells.spell_factory import get_initial_spell_deck
from game_engine.models.spells.spell_id import Spell_ID


@dataclass
class PlayerResources:
    """
    Used to display the player's game information/characteristics
    such as their HP, MP and abilities.
    """

    max_hp: int
    current_hp: int
    max_mp: int
    current_mp: int
    spells: dict[Spell_ID, int]

    @staticmethod
    def get_initial():
        return PlayerResources(
            max_hp=MAX_HP_VALUE,
            current_hp=MAX_HP_VALUE,
            max_mp=MAX_MP_VALUE,
            current_mp=1,
            spells=get_initial_spell_deck(),
        )

    def to_dto(self):
        return PlayerResourcesDto(
            maxHP=self.max_hp,
            currentHP=self.current_hp,
            maxMP=self.max_mp,
            currentMP=self.current_mp,
            spells=self.spells,
        )
