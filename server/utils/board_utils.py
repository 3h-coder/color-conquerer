"""
Contains all utility methods relative to 2D arrays.
"""


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


def is_out_of_bounds(index, board_size: int = None, square_board: list[list] = None):
    if index < 0:
        return True

    if board_size is not None:
        return index >= board_size

    if square_board:
        return index >= len(square_board[0])

    return False
