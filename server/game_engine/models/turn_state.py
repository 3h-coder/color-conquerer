from dataclasses import dataclass

from game_engine.models.actions.cell_attack import CellAttack
from game_engine.models.actions.cell_movement import CellMovement
from game_engine.models.actions.spell_casting import SpellCasting


@dataclass
class TurnState:
    """
    Holds data that persists within the duration of a turn.

    Typically used for action calculation and recording purposes.
    """

    player1_turn: bool
    attacks = list[CellAttack]
    movements = list[CellMovement]
    spells = list[SpellCasting]
