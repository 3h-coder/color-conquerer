from dataclasses import dataclass
from enum import IntEnum

from dto.coordinates_dto import CoordinatesDto
from dto.partial_match_action_dto import PartialMatchActionDto


class ActionType(IntEnum):
    CELL_MOVE = 0
    CELL_ATTACK = 1
    PLAYER_SPELL = 2


@dataclass
class MatchActionDto(PartialMatchActionDto):
    cellId: str
    isDirect: bool

    def __eq__(self, other):
        return (
            isinstance(other, MatchActionDto)
            and self.playerId == other.playerId
            and self.type == other.type
            and self.originatingCellCoords == other.originatingCellCoords
            and self.impactedCoords == other.impactedCoords
            and self.cellId == other.cellId
            and self.isDirect == other.isDirect
        )

    def __hash__(self):
        return hash(
            (
                self.playerId,
                self.isDirect,
                self.type,
                self.originatingCellCoords,
                self.impactedCoords,
                self.isDirect,
                self.cellId,
            )
        )

    @classmethod
    def cell_movement(
        cls,
        player_id,
        cell_id,
        row_index,
        column_index,
        new_row_index,
        new_column_index,
    ):
        return MatchActionDto(
            playerId=player_id,
            isDirect=True,
            type=ActionType.CELL_MOVE,
            originatingCellCoords=CoordinatesDto(row_index, column_index),
            impactedCoords=(CoordinatesDto(new_row_index, new_column_index),),
            cellId=cell_id,
        )

    @classmethod
    def cell_attack(
        cls,
        player_id,
        cell_id,
        row_index,
        column_index,
        attack_row_index,
        attack_column_index,
    ):
        return MatchActionDto(
            playerId=player_id,
            isDirect=True,
            type=ActionType.CELL_ATTACK,
            originatingCellCoords=CoordinatesDto(row_index, column_index),
            impactedCoords=(CoordinatesDto(attack_row_index, attack_column_index),),
            cellId=cell_id,
        )
