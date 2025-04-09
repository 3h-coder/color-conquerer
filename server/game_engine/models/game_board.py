from dataclasses import dataclass
from typing import Callable

from constants.game_constants import BOARD_SIZE
from game_engine.models.cell.cell import Cell
from utils.board_utils import get_neighbours


@dataclass
class GameBoard:
    """
    Grid/board in which the players play.
    """

    board: list[list[Cell]]
    is_transient: bool

    def to_dto(self, for_player1: bool | None):
        """
        Note : GameBoardDto is not defined, this simply returns a 2D CellDto array
        """
        return [[cell.to_dto(for_player1) for cell in row] for row in self.board]

    @staticmethod
    def get_initial():
        board = _create_starting_board(BOARD_SIZE)

        # Initialize the master cells
        player1_master_cell = board[1][5]
        player2_master_cell = board[9][5]

        player1_master_cell.set_owned_by_player1()
        player1_master_cell.is_master = True

        player2_master_cell.set_owned_by_player2()
        player2_master_cell.is_master = True

        # Initialize mana bubbles
        board[6][5].set_as_mana_bubble()
        board[5][1].set_as_mana_bubble()
        board[5][9].set_as_mana_bubble()

        return GameBoard(board, is_transient=False)

    def get(self, row_index: int, column_index: int):
        return self.board[row_index][column_index]

    def clone_as_transient(self):
        cloned_game_board = self.clone()
        cloned_game_board.is_transient = True
        return cloned_game_board

    def clone(self):
        cloned_board = [[cell.clone() for cell in row] for row in self.board]
        return GameBoard(cloned_board, is_transient=False)

    def get_cells_owned_by_player(self, player1: bool):
        return [
            cell
            for row in self.board
            for cell in row
            if (player1 and cell.belongs_to_player_1())
            or (not player1 and cell.belongs_to_player_2())
        ]

    def get_neighbours(self, row_index: int, column_index: int) -> list[Cell]:
        return get_neighbours(row_index, column_index, self.board)

    def get_neighbours_matching_condition(
        self, row_index: int, column_index: int, condition: Callable[[Cell], bool]
    ) -> list[Cell]:
        neighbours = self.get_neighbours(row_index, column_index)
        return [cell for cell in neighbours if condition(cell)]


def _create_starting_board(board_size: int):
    return [
        [
            Cell.get_default_idle_cell(row_index=i, col_index=j)
            for j in range(board_size)
        ]
        for i in range(board_size)
    ]
