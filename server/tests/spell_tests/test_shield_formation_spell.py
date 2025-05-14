from game_engine.models.actions.cell_movement import CellMovement
from game_engine.models.cell.cell import Cell
from game_engine.models.cell.cell_state import CellState
from game_engine.models.cell.cell_transient_state import CellTransientState
from game_engine.models.spells.spell_id import SpellId
from tests.helpers.match_helper import MatchHelper


def test_shield_formation_should_not_be_usable(started_match: MatchHelper):
    # Arrange
    player1_client, _ = started_match.get_clients()
    player1_resources, _ = (
        started_match.match_context_helper.get_both_players_resources()
    )
    player1_master_cell = started_match.get_master_cell(of_player_1=True)

    player1_resources.current_mp = 3

    # Act
    player1_client.click_spell(SpellId.SHIELD_FORMATION)

    # Assert
    transient_board = started_match.get_transient_game_board()
    assert transient_board is not None
    assert (
        transient_board.get(
            player1_master_cell.row_index, player1_master_cell.column_index
        ).transient_state
        == CellTransientState.NONE
    )


def test_shield_formation_works(started_match: MatchHelper):
    # Arrange
    player1_client, _ = started_match.get_clients()
    player1_resources, _ = (
        started_match.match_context_helper.get_both_players_resources()
    )
    player1_master_cell = started_match.get_master_cell(of_player_1=True)

    owned_cell1 = started_match.get_cell_at(
        player1_master_cell.row_index - 1, player1_master_cell.column_index
    )
    owned_cell2 = started_match.get_cell_at(
        player1_master_cell.row_index - 1, player1_master_cell.column_index + 1
    )
    owned_cell3 = started_match.get_cell_at(
        player1_master_cell.row_index, player1_master_cell.column_index + 1
    )
    owned_cell1.set_owned_by_player1()
    owned_cell2.set_owned_by_player1()
    owned_cell3.set_owned_by_player1()
    player1_resources.current_mp = 3

    # Act
    player1_client.click_spell(SpellId.SHIELD_FORMATION)

    # Assert
    transient_board = started_match.get_transient_game_board()
    assert transient_board is not None
    assert all(
        cell.transient_state == CellTransientState.CAN_BE_SPELL_TARGETTED
        for cell in transient_board.get_cells_owned_by_player(player1=True)
    )

    # Act again
    player1_client.click_cell_at(
        player1_master_cell.row_index, player1_master_cell.column_index
    )

    # Assert again
    owned_cells: list[Cell] = [
        player1_master_cell,
        owned_cell1,
        owned_cell2,
        owned_cell3,
    ]
    assert all(cell.is_shielded() for cell in owned_cells)


def test_shielded_state(started_match: MatchHelper):
    # Arrange
    player1_client, _ = started_match.get_clients()
    player1_resources, player2_resources = (
        started_match.match_context_helper.get_both_players_resources()
    )
    player1_master_cell = started_match.get_master_cell(of_player_1=True)
    player2_master_cell = started_match.get_master_cell(of_player_1=False)

    row_index, column_index = (
        player1_master_cell.row_index,
        player1_master_cell.column_index + 1,
    )
    neighbour_cell = started_match.get_cell_at(row_index, column_index)

    # Act
    # Move the player 2 master cell next to the player 1's
    CellMovement._transfer_cell(player2_master_cell, neighbour_cell)
    player1_master_cell.state = player1_master_cell.state.with_modifier(
        CellState.SHIELDED
    )

    # Attack the player 2 master cell
    player1_client.click_cell_at(
        player1_master_cell.row_index, player1_master_cell.column_index
    )
    player1_client.click_cell_at(row_index, column_index)

    # Assert
    assert not player1_master_cell.is_shielded()
    # The player 1 master cell took no damage
    assert player1_resources.current_hp == player1_resources.max_hp
    # Unlike the player 2 master cell
    assert player2_resources.current_hp == player2_resources.max_hp - 1
