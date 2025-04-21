from game_engine.models.actions.cell_attack import CellAttack
from game_engine.models.actions.cell_movement import CellMovement
from game_engine.models.actions.cell_spawn import CellSpawn
from game_engine.models.cell.cell_transient_state import CellTransientState
from tests.helpers.match_helper import MatchHelper


def test_cell_movement(started_match: MatchHelper):
    # Arrange
    player1_client, _ = started_match.get_clients()

    # Act
    player1_master_cell = started_match.get_master_cell(of_player_1=True)
    row_index, col_index = player1_master_cell.get_coordinates().as_tuple()
    # Select the master cell
    player1_client.click_cell_at(row_index, col_index)

    # Assert
    transient_game_board = started_match.get_transient_game_board()
    assert transient_game_board is not None

    player1_master_transient_cell = transient_game_board.get(row_index, col_index)
    assert player1_master_transient_cell.transient_state == CellTransientState.SELECTED

    possible_actions = started_match.get_possible_actions()
    possible_movements = [
        possible_action
        for possible_action in possible_actions
        if isinstance(possible_action, CellMovement)
    ]
    # All neighbours + 3 extra movements for north, east and west
    assert len(possible_movements) == 11

    for movement in possible_movements:
        row_index, col_index = movement.metadata.impacted_coords.as_tuple()
        transient_cell = transient_game_board.get(row_index, col_index)
        assert transient_cell.transient_state == CellTransientState.CAN_BE_MOVED_INTO

    # Act again
    chosen_movement = possible_movements[0]
    row_index, col_index = chosen_movement.metadata.impacted_coords.as_tuple()
    # Select an idle cell to move the master cell
    player1_client.click_cell_at(row_index, col_index)

    # Assert again
    assert chosen_movement in started_match.get_current_turn_processed_actions()

    assert not player1_master_cell.belongs_to_player_1()
    player1_master_cell = started_match.get_cell_at(row_index, col_index)
    assert player1_master_cell.belongs_to_player_1()
    assert player1_master_cell.is_master


def test_cell_attack(started_match: MatchHelper):
    # Arrange
    player1_resources, player2_resources = started_match.get_both_players_resources()
    player1_starting_hp = player1_resources.current_hp
    player2_starting_hp = player2_resources.current_hp

    player1_client, _ = started_match.get_clients()

    player1_master_cell = started_match.get_master_cell(of_player_1=True)
    player2_master_cell = started_match.get_master_cell(of_player_1=False)

    row_index, col_index = player1_master_cell.get_coordinates().as_tuple()
    player1_master_cell_neighbours = started_match.get_neighbours(row_index, col_index)
    player1_master_cell_neighbour = player1_master_cell_neighbours[0]

    # Move the player2 master cell next to the player1's
    CellMovement._transfer_cell(player2_master_cell, player1_master_cell_neighbour)

    # Act
    player1_client.click_cell_at(row_index, col_index)

    # Assert
    transient_game_board = started_match.get_transient_game_board()
    assert transient_game_board is not None

    possible_actions = started_match.get_possible_actions()
    possible_attacks = [
        possible_action
        for possible_action in possible_actions
        if isinstance(possible_action, CellAttack)
    ]

    assert len(possible_attacks) == 1

    chosen_attack = possible_attacks[0]
    row_index, col_index = chosen_attack.metadata.impacted_coords.as_tuple()
    transient_cell = transient_game_board.get(row_index, col_index)

    assert transient_cell.transient_state == CellTransientState.CAN_BE_ATTACKED

    # Act again
    player1_client.click_cell_at(row_index, col_index)

    # Assert again
    assert chosen_attack in started_match.get_current_turn_processed_actions()
    assert player1_resources.current_hp == player1_starting_hp - 1
    assert player2_resources.current_hp == player2_starting_hp - 1


def test_cell_spawn(started_match: MatchHelper):
    # Arrange
    player1_client, _ = started_match.get_clients()
    player1_master_cell = started_match.get_master_cell(of_player_1=True)
    player1_master_cell_neighbours = started_match.get_neighbours(
        player1_master_cell.row_index, player1_master_cell.column_index
    )

    # Act
    player1_client.click_spawn_button()

    # Assert
    transient_game_board = started_match.get_transient_game_board()
    assert transient_game_board is not None

    for neighbour in player1_master_cell_neighbours:
        transient_cell = transient_game_board.get(
            neighbour.row_index, neighbour.column_index
        )
        assert transient_cell.transient_state == CellTransientState.CAN_BE_SPAWNED_INTO

    possible_spawns = [
        action
        for action in started_match.get_possible_actions()
        if isinstance(action, CellSpawn)
    ]
    chosen_spawn = possible_spawns[0]
    row_index, col_index = chosen_spawn.metadata.impacted_coords.as_tuple()

    # Act again
    player1_client.click_cell_at(row_index, col_index)

    # Assert again
    assert chosen_spawn in started_match.get_current_turn_processed_actions()

    spawned_cell = started_match.get_cell_at(row_index, col_index)
    assert spawned_cell.belongs_to_player_1()
    assert spawned_cell.is_freshly_spawned()
