from game_engine.models.actions.cell_attack import CellAttack
from game_engine.models.actions.metadata.cell_attack_metadata import \
    CellAttackMetadata
from game_engine.models.cell.cell_transient_state import CellTransientState
from game_engine.models.dtos.coordinates import Coordinates
from game_engine.models.spells.spell_id import SpellId
from tests.helpers.match_helper import MatchHelper


def test_archer_spell_should_not_be_usable(started_match: MatchHelper):
    # Arrange
    player1_client, _ = started_match.get_clients()
    player1_master_cell = started_match.get_master_cell(of_player_1=True)
    spawn_row_index, spawn_col_index = (
        player1_master_cell.row_index - 1,
        player1_master_cell.column_index,
    )

    # Act
    player1_client.click_spawn_button()
    player1_client.click_cell_at(spawn_row_index, spawn_col_index)
    started_match.skip_n_turns(
        4
    )  # Skip 4 turns to accumulate 3 mana (player gets 2 turns)
    player1_client.click_spell(SpellId.ARCHERY_VOW)

    transient_board = started_match.get_transient_game_board()

    # Assert - spell should fail because master cell is adjacent to a non-master cell
    cells = transient_board.get_cells_owned_by_player(player1=True)
    assert all(cell.transient_state == CellTransientState.NONE for cell in cells)


def test_archer_spell_works(started_match: MatchHelper):
    # Arrange
    player1_client, _ = started_match.get_clients()
    player1_master_cell = started_match.get_master_cell(of_player_1=True)
    player2_master_cell = started_match.get_master_cell(of_player_1=False)
    spawn_row_index, spawn_col_index = (
        player1_master_cell.row_index - 1,
        player1_master_cell.column_index,
    )

    # Act
    player1_client.click_spawn_button()
    player1_client.click_cell_at(spawn_row_index, spawn_col_index)
    started_match.skip_n_turns(4)  # Skip 4 turns to accumulate 3 mana (player gets 2 turns)
    # Move the master cell away
    player1_client.click_cell_at(
        player1_master_cell.row_index, player1_master_cell.column_index
    )
    final_master_row_index = player1_master_cell.row_index + 2
    player1_client.click_cell_at(
        final_master_row_index, player1_master_cell.column_index
    )

    player1_client.click_spell(SpellId.ARCHERY_VOW)

    # Assert
    transient_board = started_match.get_transient_game_board()
    assert (
        transient_board.get(
            final_master_row_index, player1_master_cell.column_index
        ).transient_state
        == CellTransientState.NONE
    )
    assert (
        transient_board.get(spawn_row_index, spawn_col_index).transient_state
        == CellTransientState.CAN_BE_SPELL_TARGETTED
    )

    # Act again
    # Click on it to apply the spell
    player1_client.click_cell_at(spawn_row_index, spawn_col_index)
    # Click on it again to select it
    player1_client.click_cell_at(spawn_row_index, spawn_col_index)
    # Click on the player 2 master cell to attack it
    player1_client.click_cell_at(
        player2_master_cell.row_index, player2_master_cell.column_index
    )

    # Assert again
    processed_actions = started_match.get_current_turn_processed_actions()
    processed_attack = next(
        iter([action for action in processed_actions if isinstance(action, CellAttack)])
    )
    assert processed_attack is not None
    assert (
        isinstance(processed_attack.specific_metadata, CellAttackMetadata)
        and processed_attack.specific_metadata.is_ranged_attack
    )
    assert processed_attack.metadata.originating_coords == Coordinates(
        spawn_row_index, spawn_col_index
    )
    assert (
        processed_attack.metadata.impacted_coords
        == player2_master_cell.get_coordinates()
    )
