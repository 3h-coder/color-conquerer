from game_engine.models.dtos.coordinates import Coordinates
from game_engine.models.spells.spell_id import SpellId
from tests.helpers.match_helper import MatchHelper


def test_mine_trap_spell(started_match: MatchHelper):
    # Arrange
    player1_client, player2_client = started_match.get_clients()
    _, player2_resources = started_match.get_both_players_resources()

    player2_master_cell = started_match.get_master_cell(of_player_1=False)
    master_row_index, master_column_index = (
        player2_master_cell.get_coordinates().as_tuple()
    )
    row_index1, col_index1 = (master_row_index, master_column_index + 1)
    row_index2, col_index2 = (master_row_index + 1, master_column_index + 1)

    # Act
    started_match.skip_two_turns()
    player1_client.click_spell(SpellId.MINE_TRAP)
    player1_client.click_cell_at(row_index1, col_index1)

    player1_client.click_spell(SpellId.MINE_TRAP)
    player1_client.click_cell_at(row_index2, col_index2)

    # Assert
    mine_trap1 = started_match.match_context_helper.get_cell_at(row_index1, col_index1)
    mine_trap2 = started_match.match_context_helper.get_cell_at(row_index2, col_index2)
    assert mine_trap1.is_mine_trap() and mine_trap2.is_mine_trap()

    # Act again
    player1_client.end_turn(wait_for_processing=True)
    # Spawn on the mine trap
    player2_client.click_spawn_button()
    player2_client.click_cell_at(row_index1, col_index1)

    # Assert again
    # The mines have exploded
    assert not mine_trap1.is_mine_trap() and not mine_trap2.is_mine_trap()
    # The spawned cell died instantly
    assert not mine_trap1.belongs_to_player_2()
    # The player has taken 2 damage
    assert player2_resources.current_hp == player2_resources.max_hp - 2
