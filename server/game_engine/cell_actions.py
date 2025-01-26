"""
Contains the core cell mechanics methods, such as moving a cell, spawning a cell, and triggering a cell attack.
"""

from dto.server_only.cell_info_dto import CellInfoDto
from dto.server_only.match_info_dto import MatchInfoDto


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
    cell_new_coords.clear_state()


def spawn_cell(
    row_index: int, col_index: int, player1: bool, board: list[list[CellInfoDto]]
):
    """
    Spawns a cell at the given coordinates for the given player.
    """
    cell = board[row_index][col_index]
    if player1:
        cell.set_owned_by_player1()
        cell.set_freshly_spawned()
    else:
        cell.set_owned_by_player2()
        cell.set_freshly_spawned()


def trigger_cell_attack(
    attacking_row_index,
    attacking_col_index,
    target_row_index,
    target_col_index,
    match_info: MatchInfoDto,
):
    """
    Triggers an attack between two cells on the board.
    """
    board: list[list[CellInfoDto]] = match_info.boardArray
    attacking_cell: CellInfoDto = board[attacking_row_index][attacking_col_index]
    target_cell: CellInfoDto = board[target_row_index][target_col_index]

    if attacking_cell.owner == target_cell.owner:
        return

    attacking_is_master = attacking_cell.isMaster
    target_is_master = target_cell.isMaster

    player1_game_info = match_info.get_player_game_info(player1=True)
    player2_game_info = match_info.get_player_game_info(player1=False)

    attacker_game_info = (
        player1_game_info if attacking_cell.belongs_to_player_1() else player2_game_info
    )
    target_game_info = (
        player1_game_info
        if attacker_game_info == player2_game_info
        else player2_game_info
    )

    if attacking_is_master and target_is_master:
        attacker_game_info.currentHP -= 1
        target_game_info.currentHP -= 1

    elif attacking_is_master:
        attacker_game_info.currentHP -= 1
        target_cell.set_idle()  # target cell is destroyed

    elif target_is_master:
        target_game_info.currentHP -= 1
        attacking_cell.set_idle()  # attacking cell is destroyed

    else:
        attacking_cell.set_idle()
        target_cell.set_idle()

    # The following code is technically not necessary as the game should end if a player's HP reaches 0,
    # but it's a good practice to keep the board consistent.
    if attacker_game_info.currentHP <= 0:
        attacking_cell.set_idle()
    if target_game_info.currentHP <= 0:
        target_cell.set_idle()
