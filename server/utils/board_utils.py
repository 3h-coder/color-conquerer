from dto.partial_cell_info_dto import PartialCellInfoDto
from dto.server_only.cell_info_dto import CellInfoDto, CellOwner, CellState


def create_starting_board(board_size: int):
    return [
        [
            CellInfoDto(
                owner=CellOwner.NONE,
                isMaster=False,
                rowIndex=i,
                columnIndex=j,
                state=CellState.AVAILABLE,
                id=None,
            )
            for j in range(board_size)
        ]
        for i in range(board_size)
    ]


def to_client_board_dto(board: list[list[CellInfoDto]]):
    """
    Converts a board of CellInfoDto objects to PartialCellInfoDto to be sent to the client.
    """
    result: list[list[PartialCellInfoDto]] = []
    for row in board:
        new_row = []
        for cell in row:
            new_row.append(PartialCellInfoDto.from_cell_info_dto(cell))
        result.append(new_row)

    return result


def display_board_owners(board: list[list[CellInfoDto]]):
    for row in board:
        row_display = "|".join(str(cell.owner) for cell in row)
        print(f"|{row_display}|")
        print("_" * (2 * len(row)))


def is_owned(row_index: int, col_index: int, board: list[list[CellInfoDto]]):
    return board[row_index][col_index].is_owned()


def move_cell(
    row_index: int,
    col_index: int,
    new_row_index: int,
    new_col_index: int,
    board: list[list[CellInfoDto]],
):
    """
    Moves a cell from the given original coordinates to the given new coordinates.

    This method does nothing if the cell to move is idle, and leaves an idle cell at the original coordinates otherwise.
    """
    cell_original_coords = board[row_index][col_index]

    if not cell_original_coords.is_owned():
        return

    cell_new_coords = board[new_row_index][new_col_index]
    cell_id = cell_original_coords.id
    is_master = cell_original_coords.isMaster

    if cell_original_coords.belongs_to_player_1():
        cell_new_coords.set_owned_by_player1(cell_id)
        cell_new_coords.isMaster = is_master

    elif cell_original_coords.belongs_to_player_2():
        cell_new_coords.set_owned_by_player2(cell_id)
        cell_new_coords.isMaster = is_master

    cell_original_coords.set_idle()


def is_out_of_bounds(index, board_size: int = None, square_board: list[list] = None):
    if index < 0:
        return True

    if board_size:
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
