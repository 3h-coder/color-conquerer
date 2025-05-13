from game_engine.models.actions.cell_movement import CellMovement
from game_engine.models.cell.cell_state import CellState
from game_engine.models.cell.cell_transient_state import CellTransientState
from game_engine.models.spells.spell_id import SpellId
from tests.helpers.match_helper import MatchHelper


def test_celerity_spell_should_not_be_usable(started_match: MatchHelper):
    # Arrange
    player1_client, _ = started_match.get_clients()

    # Act
    player1_client.click_spell(SpellId.CELERITY)
    transient_board = started_match.get_transient_game_board()

    # Assert
    assert transient_board is not None
    player1_master_cell = next(
        iter(transient_board.get_cells_owned_by_player(player1=True))
    )
    assert (
        player1_master_cell.transient_state != CellTransientState.CAN_BE_SPELL_TARGETTED
    )


def test_celerity_spell_works(started_match: MatchHelper):
    # Arrange
    player1_client, _ = started_match.get_clients()
    player1_master_cell = started_match.get_master_cell(of_player_1=True)

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
    transient_board = started_match.get_transient_game_board()

    # Assert
    assert transient_board is not None
    assert (
        transient_board.get(neighbour_row_index, neighbour_column_index).transient_state
        == CellTransientState.CAN_BE_SPELL_TARGETTED
    )
    assert (
        transient_board.get(master_row_index, master_column_index).transient_state
        == CellTransientState.CAN_BE_SPELL_TARGETTED
    )

    # Act again
    player1_client.click_cell_at(master_row_index, master_column_index)

    # Assert again
    assert player1_master_cell.is_accelerated() and neighbour_cell.is_accelerated()


def test_accelerated_state(started_match: MatchHelper):
    # Arrange
    player1_client, _ = started_match.get_clients()
    player1_master_cell = started_match.get_master_cell(of_player_1=True)
    player2_master_cell = started_match.get_master_cell(of_player_1=False)
    player1_master_cell_neighbour_row_index, player1_master_cell_neighbour_col_index = (
        player1_master_cell.row_index + 1,
        player1_master_cell.column_index + 1,
    )
    final_row_index, final_col_index = (
        player1_master_cell.row_index + 2,
        player1_master_cell.column_index + 2,
    )

    # Act
    CellMovement._transfer_cell(
        player2_master_cell,
        started_match.get_cell_at(
            player1_master_cell_neighbour_row_index,
            player1_master_cell_neighbour_col_index,
        ),
    )
    player1_master_cell.state = player1_master_cell.state.with_modifier(
        CellState.ACCELERATED
    )

    player1_client.click_cell_at(
        player1_master_cell.row_index, player1_master_cell.column_index
    )
    # Move once
    player1_client.click_cell_at(final_row_index, player1_master_cell.column_index)
    # Attack one
    player1_client.click_cell_at(
        player1_master_cell_neighbour_row_index, player1_master_cell_neighbour_col_index
    )
    # Move again
    player1_client.click_cell_at(final_row_index, final_col_index)
    # Attack again
    player1_client.click_cell_at(
        player1_master_cell_neighbour_row_index, player1_master_cell_neighbour_col_index
    )

    # Assert
    player1_resources, player2_resources = started_match.get_both_players_resources()
    assert player1_resources.current_hp == player1_resources.max_hp - 2
    assert player2_resources.current_hp == player2_resources.max_hp - 2
