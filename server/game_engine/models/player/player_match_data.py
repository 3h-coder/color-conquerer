from dataclasses import dataclass


@dataclass
class PlayerMatchData:
    """
    Stores data and states tied to a player during a match.
    """

    # The amount of damage the player should take due to fatigue
    # This is incremented every turn the player has 0 stamina
    fatigue_damage: int

    @staticmethod
    def get_initial():
        return PlayerMatchData(fatigue_damage=0)
