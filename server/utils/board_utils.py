"""
Contains all utility methods relative to the game board, excluding game engine mechanics
and cell manipulation.
"""

from dto.cell_info_dto import Cell, CellDto


def create_starting_board(board_size: int):
    return [
        [
            Cell.get_default_idle_cell(row_index=i, col_index=j)
            for j in range(board_size)
        ]
        for i in range(board_size)
    ]


def copy_board(board: list[list[Cell]]):
    return [[cell.clone() for cell in row] for row in board]


def to_client_board_dto(board: list[list[Cell]]):
    """
    Converts a board of Cell objects to PartialCell to be sent to the client.
    """
    result: list[list[Cell]] = []
    for row in board:
        new_row = []
        for cell in row:
            new_row.append(CellDto.from_cell(cell))
        result.append(new_row)

    return result


def get_cells_owned_by_player(player1: bool, board: list[list[Cell]]):
    """
    Returns a list of cells owned by the given player.
    """
    return [
        cell
        for row in board
        for cell in row
        if (player1 and cell.belongs_to_player_1())
        or (not player1 and cell.belongs_to_player_2())
    ]


def is_owned(row_index: int, col_index: int, board: list[list[Cell]]):
    return board[row_index][col_index].is_owned()


def is_out_of_bounds(index, board_size: int = None, square_board: list[list] = None):
    if index < 0:
        return True

    if board_size is not None:
        return index >= board_size

    if square_board:
        return index >= len(square_board[0])

    return False


def get_neighbours(row_index: int, column_index: int, board: list[list]):
    directions = [
        (-1, 0),  # down
        (1, 0),  # up
        (0, -1),  # left
        (0, 1),  # right
        (-1, -1),  # bottom-left
        (-1, 1),  # bottom-right
        (1, -1),  # top-left
        (1, 1),  # top-right
    ]

    neighbors = []

    for dr, dc in directions:
        r, c = row_index + dr, column_index + dc
        # Check if the neighbor is within bounds
        if 0 <= r < len(board) and 0 <= c < len(board[0]):
            neighbors.append(board[r][c])

    return neighbors
