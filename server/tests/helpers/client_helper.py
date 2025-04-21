from events.events import Events
from game_engine.models.cell.cell import Cell
from server import Server
from tests.utilities.mocks import mock_queue_player_dto
from tests.utilities.utilities import initialize_session


class ClientHelper:
    """
    Helper class to simulate an actual client.
    """

    def __init__(self, server: Server):
        self._server = server
        self._app = server.app
        self._flask_client = self._app.test_client()
        # ⚠️ The session must be initialized before creating the socketio
        # test client
        initialize_session(self._flask_client)
        self._socketio_client = server.socketio.test_client(
            app=self._app, flask_test_client=self._flask_client
        )

    def refresh(self):
        self._socketio_client = self._server.socketio.test_client(
            app=self._app, flask_test_client=self._flask_client
        )

    # region Wrapped methods

    def get(self, route: str):
        self._flask_client.get(route)

    def emit(self, event: str, *args, **kwargs):
        self._socketio_client.emit(event, *args, **kwargs)

    # endregion

    # region Match methods

    def register_for_match(self):
        queue_player_dto = mock_queue_player_dto()
        self.emit(Events.CLIENT_QUEUE_REGISTER, queue_player_dto.to_dict())

    def send_ready_signal(self):
        self.emit(Events.CLIENT_READY)

    def end_turn(self):
        self.emit(Events.CLIENT_TURN_END)

    def concede(self):
        self.emit(Events.CLIENT_MATCH_CONCEDE)

    def request_spells(self):
        self.emit(Events.CLIENT_REQUEST_SPELLS)

    def click_any_cell(self):
        cell_dto = Cell.get_default_idle_cell(0, 0).to_dto(None)
        self.emit(Events.CLIENT_CELL_CLICK, cell_dto.to_dict())

    def click_any_spell(self):
        self.emit(Events.CLIENT_SPELL_BUTTON, 1)

    def click_spawn_button(self):
        self.emit(Events.CLIENT_SPAWN_BUTTON)

    # endregion

    # region Private methods

    # endregion
