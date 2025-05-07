from enum import IntEnum


class SpellId(IntEnum):
    MINE_TRAP = 1
    SHIELD_FORMATION = 2
    CELERITY = 3
    ARCHERY_VOW = 4
    AMBUSH = 5

    def __repr__(self):
        return self.name
