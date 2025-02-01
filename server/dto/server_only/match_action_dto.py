from dataclasses import dataclass
from enum import IntEnum

from dto.coordinates_dto import CoordinatesDto
from dto.partial_match_action_dto import PartialMatchActionDto
from game_engine.spells.spell_base import SpellBase


class ActionType(IntEnum):
    CELL_MOVE = 0
    CELL_ATTACK = 1
    CELL_SPAWN = 2
    PLAYER_SPELL = 3


@dataclass
class MatchActionDto(PartialMatchActionDto):
    cellId: str
    isDirect: bool
    manaCost: int

    def __str__(self):
        player_str = "Player 1" if self.player1 else "Player 2"
        return (
            f"{player_str} | {self.type.name}\n"
            f"{self.originatingCellCoords} -> {self.impactedCoords}\n"
            f"cellId: {self.cellId}, manaCost: {self.manaCost}"
        )

    def __eq__(self, other):
        return (
            isinstance(other, MatchActionDto)
            and self.player1 == other.player1
            and self.type == other.type
            and self.originatingCellCoords == other.originatingCellCoords
            and self.impactedCoords == other.impactedCoords
            and self.spellId == other.spellId
            and self.cellId == other.cellId
            and self.isDirect == other.isDirect
            and self.manaCost == other.manaCost
        )

    def __hash__(self):
        return hash(
            (
                self.player1,
                self.isDirect,
                self.type,
                self.originatingCellCoords,
                self.impactedCoords,
                self.spellId,
                self.cellId,
                self.isDirect,
                self.manaCost,
            )
        )

    @staticmethod
    def cell_movement(
        player1,
        cell_id,
        row_index,
        column_index,
        new_row_index,
        new_column_index,
    ):
        return MatchActionDto(
            player1=player1,
            isDirect=True,
            type=ActionType.CELL_MOVE,
            originatingCellCoords=CoordinatesDto(row_index, column_index),
            impactedCoords=CoordinatesDto(new_row_index, new_column_index),
            spellId=None,
            cellId=cell_id,
            manaCost=0,
        )

    @staticmethod
    def cell_attack(
        player1,
        cell_id,
        row_index,
        column_index,
        attack_row_index,
        attack_column_index,
    ):
        return MatchActionDto(
            player1=player1,
            isDirect=True,
            type=ActionType.CELL_ATTACK,
            originatingCellCoords=CoordinatesDto(row_index, column_index),
            impactedCoords=CoordinatesDto(attack_row_index, attack_column_index),
            spellId=None,
            cellId=cell_id,
            manaCost=0,
        )

    @staticmethod
    def cell_spawn(player1, row_index, column_index):
        return MatchActionDto(
            player1=player1,
            isDirect=True,
            type=ActionType.CELL_SPAWN,
            originatingCellCoords=None,
            impactedCoords=CoordinatesDto(row_index, column_index),
            spellId=None,
            cellId=None,
            manaCost=1,
        )

    @staticmethod
    def spell(player1, spell: SpellBase, row_index, column_index):
        return MatchActionDto(
            player1=player1,
            isDirect=True,
            type=ActionType.PLAYER_SPELL,
            originatingCellCoords=None,
            impactedCoords=CoordinatesDto(row_index, column_index),
            spellId=spell.id,
            cellId=None,
            manaCost=spell.mana_cost,
        )
