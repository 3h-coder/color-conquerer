from dto.coordinates_dto import CoordinatesDto
from game_engine.models.cell.cell_owner import CellOwner
from game_engine.models.game_board import GameBoard
from game_engine.models.spells.spell import Spell
from game_engine.models.spells.spell_id import SpellId


class ShieldFormationSpell(Spell):
    ID = SpellId.SHIELD_FORMATION
    NAME = "Shield formation"
    DESCRIPTION = "Select a square cell formation to apply a shield " "to each."
    MANA_COST = 3

    def get_possible_targets(self, transient_board: "GameBoard"):
        possible_targets = []

        return possible_targets

    def invoke(
        self, coordinates: set[CoordinatesDto], board: "GameBoard", invocator: CellOwner
    ):
        pass  # nothing for now
