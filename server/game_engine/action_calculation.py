from config.logging import get_configured_logger
from game_engine.models.actions.cell_attack import CellAttack
from game_engine.models.actions.cell_movement import CellMovement
from game_engine.models.actions.cell_spawn import CellSpawn
from game_engine.models.actions.spell_casting import SpellCasting
from game_engine.models.cell.cell import Cell
from game_engine.models.game_board import GameBoard
from game_engine.models.spells.abstract.spell import Spell
from game_engine.models.turn.turn_state import TurnState

_logger = get_configured_logger(__name__)


def get_possible_movements_and_attacks(
    player1: bool, cell: Cell, transient_board: GameBoard, turn_state: TurnState
):
    if cell.is_freshly_spawned():
        return set()

    movements: set[CellMovement] = set()
    attacks: set[CellAttack] = set()
    if not _has_already_moved_this_turn(cell, turn_state):
        movements = CellMovement.calculate(cell, player1, transient_board)

    if not _has_already_attacked_this_turn(cell, turn_state):
        attacks = CellAttack.calculate(cell, player1, transient_board)

    return movements.union(attacks)


def get_possible_spawns(player1: bool, transient_board: GameBoard):
    return CellSpawn.calculate(player1, transient_board)


def get_possible_spell_castings(
    spell: Spell, player1: bool, transient_board: GameBoard
):
    return SpellCasting.calculate(spell, player1, transient_board)


def _has_already_moved_this_turn(cell: Cell, turn_state: TurnState):
    if cell.id not in turn_state.movements:
        return False

    if cell.is_accelerated():
        return turn_state.movements[cell.id] == 2

    return turn_state.movements[cell.id] == 1


def _has_already_attacked_this_turn(cell: Cell, turn_state: TurnState):
    if cell.id not in turn_state.attacks:
        return False

    if cell.is_accelerated():
        return turn_state.attacks[cell.id] == 2
    return turn_state.attacks[cell.id] == 1
