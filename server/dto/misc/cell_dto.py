from dataclasses import dataclass

from dto.base_dto import BaseDto
from game_engine.models.cell.cell_hidden_state import CellHiddenState
from game_engine.models.cell.cell_owner import CellOwner
from game_engine.models.cell.cell_state import CellState
from game_engine.models.cell.cell_transient_state import CellTransientState


@dataclass
class CellDto(BaseDto):
    owner: CellOwner
    isMaster: bool
    rowIndex: int
    columnIndex: int
    state: CellState
    # Note : hidden states should be equal to 0 (NONE) if the
    # cell does not belong to the player
    hiddenState: CellHiddenState
    transientState: CellTransientState
