import time

from events.events import Events
from game_engine.models.cell.cell import Cell
from game_engine.models.spells.spell_id import SpellId
from server import Server
from tests.utilities.mocks import mock_queue_player_dto
from tests.utilities.utilities import initialize_session


class ClientHelper:
    """
    Helper class to simulate an actual client.
    """

    def __init__(self, server: Server, is_player1: bool):
        self._is_player1 = is_player1
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

    def disconnect(self):
        self._socketio_client.disconnect()

    def connect(self):
        self._socketio_client.connect()

    # endregion

    # region Match methods

    def register_for_match(self):
        queue_player_dto = mock_queue_player_dto()
        self.emit(Events.CLIENT_QUEUE_REGISTER, queue_player_dto.to_dict())

    def send_ready_signal(self):
        self.emit(Events.CLIENT_READY)

    def end_turn(self, wait_for_processing=False):
        self.emit(Events.CLIENT_TURN_END)
        if wait_for_processing:
            time.sleep(0.01)

    def concede(self):
        self.emit(Events.CLIENT_MATCH_CONCEDE)

    def click_any_cell(self):
        self.click_cell_at(0, 0)

    def click_cell_at(self, row_index: int, col_index: int):
        cell_dto = Cell.get_default_idle_cell(row_index, col_index).to_dto(
            self._is_player1
        )
        self.emit(Events.CLIENT_CELL_CLICK, cell_dto.to_dict())

    def click_any_spell(self):
        self.click_spell(1)

    def click_spawn_button(self):
        self.emit(Events.CLIENT_SPAWN_BUTTON)

    def click_spell(self, spell_id: SpellId):
        self.emit(Events.CLIENT_SPELL_BUTTON, spell_id)

    # endregion
