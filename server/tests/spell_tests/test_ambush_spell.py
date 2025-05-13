from game_engine.models.actions.cell_movement import CellMovement
from game_engine.models.spells.spell_id import SpellId
from tests.helpers.match_helper import MatchHelper


def test_ambush_spell_enemy_side(started_match: MatchHelper):
    # Arrange
    player1_client, _ = started_match.get_clients()
    player2_master_cell = started_match.get_master_cell(of_player_1=False)
    enemy_row_index, enemy_col_index = player2_master_cell.get_coordinates().as_tuple()

    # Act
    started_match.skip_two_turns()
    player1_client.click_spell(SpellId.AMBUSH)
    player1_client.click_cell_at(enemy_row_index, enemy_col_index)

    # Assert
    enemy_cell_neighbours = started_match.get_neighbours(
        enemy_row_index, enemy_col_index
    )
    spawned_cells = [
        cell for cell in enemy_cell_neighbours if cell.belongs_to_player_1()
    ]

    assert len(spawned_cells) == 3


def test_ambush_spell_friendly_side(started_match: MatchHelper):
    # Arrange
    player1_client, _ = started_match.get_clients()
    player1_master_cell = started_match.get_master_cell(of_player_1=True)
    player2_master_cell = started_match.get_master_cell(of_player_1=False)
    random_neighbour = next(
        iter(
            started_match.get_neighbours(
                player1_master_cell.row_index, player1_master_cell.column_index
            )
        )
    )
    enemy_row_index, enemy_col_index = random_neighbour.get_coordinates().as_tuple()

    # Act
    # Move the player 2 master cell next to the player 1's
    CellMovement._transfer_cell(player2_master_cell, random_neighbour)
    started_match.skip_two_turns()
    player1_client.click_spell(SpellId.AMBUSH)
    player1_client.click_cell_at(
        random_neighbour.row_index, random_neighbour.column_index
    )

    # Assert
    enemy_cell_neighbours = started_match.get_neighbours(
        enemy_row_index, enemy_col_index
    )
    spawned_cells = [
        cell
        for cell in enemy_cell_neighbours
        if cell.belongs_to_player_1() and not cell.is_master
    ]
    assert len(spawned_cells) == 2
