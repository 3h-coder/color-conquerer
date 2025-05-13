from game_engine.models.actions.cell_movement import CellMovement
from game_engine.models.spells.spell_id import SpellId
from tests.helpers.match_helper import MatchHelper


def test_celerity_spell(started_match: MatchHelper):
    # Arrange
    player1_client, _ = started_match.get_clients()
    player1_master_cell = started_match.get_master_cell(of_player_1=True)
    player2_master_cell = started_match.get_master_cell(of_player_1=False)

    master_row_index, master_column_index = (
        player1_master_cell.get_coordinates().as_tuple()
    )
    neighbour_row_index, neighbour_column_index = (
        master_row_index + 1,
        master_column_index + 1,
    )
    neighbour_cell = started_match.match_context_helper.get_cell_at(
        neighbour_row_index, neighbour_column_index
    )

    # Act
    player1_client.click_spawn_button()
    player1_client.click_cell_at(neighbour_row_index, neighbour_column_index)
    started_match.skip_n_turns(2)

    player1_client.click_spell(SpellId.CELERITY)
    player1_client.click_cell_at(master_row_index, master_column_index)

    # Assert
    assert player1_master_cell.is_accelerated() and neighbour_cell.is_accelerated()

    # Arrange again
    final_master_row_index, final_master_column_index = (
        master_row_index + 2,
        master_column_index + 2,
    )
    enemy_cell_row_index, enemy_cell_col_index = (
        final_master_row_index + 1,
        final_master_column_index,
    )
    enemy_cell = started_match.match_context_helper.get_cell_at(
        enemy_cell_row_index, enemy_cell_col_index
    )

    # Move the player2 master cell next to the player1's (after the latter moves)
    CellMovement._transfer_cell(player2_master_cell, enemy_cell)

    # Act again
    # Select the master cell
    player1_client.click_cell_at(master_row_index, master_column_index)
    # Move it upwards
    player1_client.click_cell_at(final_master_row_index, master_column_index)
    # Move it to the right (The second movement should only be possible because the cell is accelerated)
    player1_client.click_cell_at(final_master_row_index, final_master_column_index)

    new_player1_master_cell = started_match.match_context_helper.get_cell_at(
        final_master_row_index, final_master_column_index
    )

    # Assert again
    assert (
        new_player1_master_cell.belongs_to_player_1()
        and new_player1_master_cell.is_master
    )

    # Arrange again
    player2_master_cell = started_match.match_context_helper.get_cell_at(
        enemy_cell_row_index, enemy_cell_col_index
    )

    # Act again
    # Attack the enemy master cell
    player1_client.click_cell_at(enemy_cell_row_index, enemy_cell_col_index)
    # Attack the enemy master cell 2
    player1_client.click_cell_at(enemy_cell_row_index, enemy_cell_col_index)

    # Assert again
    player1_resources, player2_resources = started_match.get_both_players_resources()
    assert player1_resources.current_hp == player1_resources.max_hp - 2
    assert player2_resources.current_hp == player2_resources.max_hp - 2
