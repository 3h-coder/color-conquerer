from dataclasses import dataclass

from game_engine.models.cell.cell_hidden_state import CellHiddenState
from game_engine.models.cell.cell_owner import CellOwner


@dataclass
class CellHiddenStateInfo:
    state: CellHiddenState
    visible_to: CellOwner

    @staticmethod
    def default():
        return CellHiddenStateInfo(
            state=CellHiddenState.NONE, visible_to=CellOwner.NONE
        )

    def clone(self):
        return CellHiddenStateInfo(self.state, self.visible_to)

    def reset(self):
        self.state = CellHiddenState.NONE
        self.visible_to = CellOwner.NONE

    def is_visible_to_player1(self):
        return self.visible_to == CellOwner.PLAYER_1

    def is_visible_to_player2(self):
        return self.visible_to == CellOwner.PLAYER_2

    def is_visible_to_both(self):
        return self.visible_to == CellOwner.BOTH

    def is_mine_trap(self):
        return self.state == CellHiddenState.MINE_TRAP
