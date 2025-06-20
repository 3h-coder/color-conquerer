from handlers.match_handler_unit import MatchHandlerUnit
from tests.helpers.client_helper import ClientHelper
from tests.helpers.match_context_helper import MatchContextHelper
from tests.utilities.mocks import mock_server


class MatchHelper:
    """
    Helper class to simulate a real match between 2 players.
    """

    def __init__(self):
        self.server = mock_server()
        self.player1_client = ClientHelper(self.server, is_player1=True)
        self.player2_client = ClientHelper(self.server, is_player1=False)
        self.match_handler_unit: MatchHandlerUnit | None = None
        self.match_context_helper: MatchContextHelper | None = None
        self._set_up_server_for_tests()

    def initiate(self):
        # ⚠️ The order is important
        self.player1_client.register_for_match()
        self.player2_client.register_for_match()

        closed_room = next(iter(self.server.room_handler.closed_rooms.values()))
        self._set_match(self.server.match_handler.get_unit(closed_room.id))

        assert self.match_handler_unit.is_waiting_to_start()

    def start(self):
        if self.match_handler_unit is None:
            self.initiate()

        self.player1_client.send_ready_signal()
        self.player2_client.send_ready_signal()

        assert self.match_handler_unit.is_ongoing()

    def skip_two_turns(self):
        self.skip_n_turns(2)

    def skip_n_turns(self, number: int):
        """
        Have both clients successively end their turns for the given number parameter.
        """
        player1_client, player2_client = self.get_clients()
        for i in range(number):
            current_client = None
            if self.get_current_turn() % 2 == 0:
                current_client = player2_client
            else:
                current_client = player1_client
            current_client.end_turn(wait_for_processing=True)

    # region Getters

    def get_clients(self):
        return self.player1_client, self.player2_client

    def get_current_turn(self):
        return self.match_context_helper.get_current_turn()

    def get_current_player(self):
        return self.match_context_helper.get_current_player()

    def get_both_players_resources(self):
        return self.match_context_helper.get_both_players_resources()

    def get_both_player_match_data(self):
        return self.match_context_helper.get_both_player_match_data()

    def get_master_cell(self, of_player_1: bool):
        return self.match_context_helper.get_master_cell(of_player_1)

    def get_neighbours(self, row_index: int, col_index: int):
        return self.match_context_helper.get_neighbours(row_index, col_index)

    def get_cell_at(self, row_index: int, col_index: int):
        return self.match_context_helper.get_cell_at(row_index, col_index)

    def get_transient_game_board(self):
        return (
            self.match_handler_unit._match_actions_service.transient_turn_state.transient_game_bard
        )

    def get_possible_actions(self):
        return (
            self.match_handler_unit._match_actions_service.transient_turn_state.possible_actions
        )

    def get_current_turn_processed_actions(self):
        actions_per_turn = (
            self.match_handler_unit._match_actions_service.actions_per_turn
        )
        return actions_per_turn.get(self.get_current_turn())

    # endregion

    # region Setters

    def set_inactivity_delays(
        self, first_in_s: int | float, second_in_s: int | float, third_in_s: int | float
    ):
        inactivity_watcher_service = (
            self.match_handler_unit._player_inactivity_watcher_service
        )
        inactivity_watcher_service._first_warning_delay_in_s = first_in_s
        inactivity_watcher_service._final_warning_delay_in_s = second_in_s
        inactivity_watcher_service._kick_delay_in_s = third_in_s

    def set_exit_delay(self, exit_delay_in_s: int | float):
        exit_watcher_service = self.match_handler_unit._player_exit_watcher_service
        exit_watcher_service._exit_delay_in_s = exit_delay_in_s

    def _set_match(self, match_handler_unit: MatchHandlerUnit):
        self.match_handler_unit = match_handler_unit
        self.match_context_helper = MatchContextHelper(match_handler_unit.match_context)
        self._set_up_match_for_tests()

    def _set_up_match_for_tests(self):
        # This will cancel automatic turn swapping for tests
        self.match_handler_unit._turn_watcher_service.turn_duration_in_s = None

    def _set_up_server_for_tests(self):
        # This will prevent the wait during the queue process
        self.server.match_handler._sleep_duration_in_s_after_opponent_found = 0

    # endregion
