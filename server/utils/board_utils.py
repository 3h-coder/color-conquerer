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


def manhattan_distance(row1: int, col1: int, row2: int, col2: int) -> int:
    """
    Calculates Manhattan distance between two coordinates.

    Args:
        row1: Row index of first position
        col1: Column index of first position
        row2: Row index of second position
        col2: Column index of second position

    Returns:
        Manhattan distance (sum of absolute differences)
    """
    return abs(row1 - row2) + abs(col1 - col2)


def get_diagonal_formations(
    start_row: int, start_col: int, valid_coords: set[tuple[int, int]]
) -> tuple[list[tuple[int, int]], list[tuple[int, int]]]:
    """
    Finds diagonal formations passing through a given coordinate.
    Returns both diagonals that pass through the starting position.

    Args:
        start_row: Starting row index
        start_col: Starting column index
        valid_coords: Set of (row, col) tuples representing valid positions

    Returns:
        Tuple of two lists: (diagonal1, diagonal2) where:
        - diagonal1: top-left to bottom-right diagonal
        - diagonal2: bottom-left to top-right diagonal
        Each list contains (row, col) tuples, empty if less than 2 cells
    """
    # Diagonal 1: top-left to bottom-right (↘)
    diagonal1 = []
    # Start from current position and go down-right
    r, c = start_row, start_col
    while (r, c) in valid_coords:
        diagonal1.append((r, c))
        r += 1
        c += 1
    # Go back and check up-left from starting position
    r, c = start_row - 1, start_col - 1
    while (r, c) in valid_coords:
        diagonal1.insert(0, (r, c))
        r -= 1
        c -= 1

    # Diagonal 2: bottom-left to top-right (↗)
    diagonal2 = []
    # Start from current position and go up-right
    r, c = start_row, start_col
    while (r, c) in valid_coords:
        diagonal2.append((r, c))
        r -= 1
        c += 1
    # Go back and check down-left from starting position
    r, c = start_row + 1, start_col - 1
    while (r, c) in valid_coords:
        diagonal2.insert(0, (r, c))
        r += 1
        c -= 1

    # Only return diagonals with at least 2 cells
    if len(diagonal1) < 2:
        diagonal1 = []
    if len(diagonal2) < 2:
        diagonal2 = []

    return diagonal1, diagonal2
