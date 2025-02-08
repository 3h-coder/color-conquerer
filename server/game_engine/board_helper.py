from constants.game_constants import BOARD_SIZE
from game_engine.models.cell import Cell


def create_starting_board_array():
    # ⚠️ the board size must never change
    # TODO: create unit tests to ensure that

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

    return board


def _create_starting_board(board_size: int):
    return [
        [
            Cell.get_default_idle_cell(row_index=i, col_index=j)
            for j in range(board_size)
        ]
        for i in range(board_size)
    ]
