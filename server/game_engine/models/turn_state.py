from dataclasses import dataclass

from game_engine.models.player_resources import PlayerResources
from game_engine.models.spells.spell_id import Spell_ID


@dataclass
class TurnState:
    """
    Holds data that persists within the duration of a turn.

    Typically used for action calculation and recording purposes.
    """

    is_player1_turn: bool
    # List of the ids of the cells that attacked this turn
    attacks: list[str]
    # List of the ids of the cells that moved this turn
    movements: list[str]
    # List of the ids of the cells that were casted this turn
    spells: list[Spell_ID]
    player1_resources: PlayerResources
    player2_resources: PlayerResources

    def reset_for_new_turn(self):
        self.is_player1_turn = not self.is_player1_turn
        self.attacks = []
        self.movements = []
        self.spells = []

    @staticmethod
    def get_initial(
        player1_turn: bool,
        player1_resources: PlayerResources,
        player2_resources: PlayerResources,
    ):
        return TurnState(
            is_player1_turn=player1_turn,
            attacks=[],
            movements=[],
            spells=[],
            player1_resources=player1_resources,
            player2_resources=player2_resources,
        )
