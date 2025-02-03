from dataclasses import dataclass

from game_engine.models.spells.spell_id import Spell_ID


@dataclass
class PlayerResources:
    max_hp: int
    current_hp: int
    max_mp: int
    current_mp: int
    spells: dict[Spell_ID, int]
