from dataclasses import dataclass
from enum import IntEnum
from typing import TYPE_CHECKING

from dto.base_dto import BaseDto
from game_engine.models.cell import Cell, CellOwner, CellState, CellTransientState


@dataclass
class CellDto(BaseDto):
    owner: CellOwner
    isMaster: bool
    rowIndex: int
    columnIndex: int
    state: CellState
    transientState: CellTransientState

    @staticmethod
    def from_cell(cell: Cell):
        return CellDto(
            cell.owner,
            cell.is_master,
            cell.row_index,
            cell.column_index,
            cell.state,
            cell.transient_state,
        )
