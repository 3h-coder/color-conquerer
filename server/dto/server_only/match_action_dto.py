from dataclasses import dataclass
from enum import IntEnum

from dto.coordinates_dto import CoordinatesDto
from dto.partial_match_action_dto import PartialMatchActionDto


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

    def __eq__(self, other):
        return (
            isinstance(other, MatchActionDto)
            and self.player1 == other.player1
            and self.type == other.type
            and self.originatingCellCoords == other.originatingCellCoords
            and self.impactedCoords == other.impactedCoords
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
                self.isDirect,
                self.cellId,
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
            impactedCoords=(CoordinatesDto(new_row_index, new_column_index),),
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
            impactedCoords=(CoordinatesDto(attack_row_index, attack_column_index),),
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
            impactedCoords=(CoordinatesDto(row_index, column_index),),
            cellId=None,
            manaCost=1,
        )
