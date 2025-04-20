from handlers.match_handler_unit import MatchHandlerUnit
from tests.helpers.client_helper import ClientHelper
from tests.utilities.mocks import mock_server


class MatchHelper:
    """
    Helper class to simulate a real match between 2 players.
    """

    def __init__(self):
        self.server = mock_server()
        self.player1_client = ClientHelper(self.server)
        self.player2_client = ClientHelper(self.server)
        self.match: MatchHandlerUnit | None = None

    def start(self):
        # ⚠️ The order is important
        self.player1_client.register_for_match()
        self.player2_client.register_for_match()

        closed_room = next(iter(self.server.room_handler.closed_rooms.values()))
        self._set_match(self.server.match_handler.get_unit(closed_room.id))

        assert self.match.is_waiting_to_start()

        self.player1_client.send_ready_signal()
        self.player2_client.send_ready_signal()

        assert self.match.is_ongoing()

    def wait_for_turn_swap_completion(self):
        turn_swap_commplete_event = (
            self.match._turn_watcher_service.turn_swap_complete_event
        )
        turn_swap_commplete_event.wait(timeout=0.01)

    # region Getters

    def get_clients(self):
        return self.player1_client, self.player2_client

    def get_current_turn(self):
        return self.match.match_context.current_turn

    # endregion

    # region Setters

    def _set_match(self, match: MatchHandlerUnit):
        self.match = match
        # This will cancel automatic turn swapping for tests
        self.match._turn_watcher_service.turn_duration_in_s = None

    # endregion
