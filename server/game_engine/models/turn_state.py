from dataclasses import dataclass

from game_engine.models.player_resources import PlayerResources
from game_engine.models.spells.spell_id import SpellId


@dataclass
class TurnState:
    """
    Holds data that persists within the duration of a turn.

    Typically used for action calculation and recording purposes.
    """

    is_player1_turn: bool
    # Cells that attacked this turn, [key,value] = [cell_id, number of attacks]
    attacks: dict[str, int]
    # Cells that moved this turn, [key,value] = [cell_id, number of movements]
    movements: dict[str, int]
    # List of the ids of the cells that were casted this turn
    spells: list[SpellId]
    player1_resources: PlayerResources
    player2_resources: PlayerResources

    def reset_for_new_turn(self):
        self.is_player1_turn = not self.is_player1_turn
        self.attacks = {}
        self.movements = {}
        self.spells = []

    def register_attack(self, cell_id: str):
        self._internal_register(cell_id, self.attacks)

    def register_movement(self, cell_id: str):
        self._internal_register(cell_id, self.movements)

    @staticmethod
    def get_initial(
        player1_turn: bool,
        player1_resources: PlayerResources,
        player2_resources: PlayerResources,
    ):
        return TurnState(
            is_player1_turn=player1_turn,
            attacks={},
            movements={},
            spells=[],
            player1_resources=player1_resources,
            player2_resources=player2_resources,
        )

    def _internal_register(self, cell_id: str, dictionary: dict[str, int]):
        if cell_id not in dictionary:
            dictionary[cell_id] = 1
        else:
            dictionary[cell_id] += 1
