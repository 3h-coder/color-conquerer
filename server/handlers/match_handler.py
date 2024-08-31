from config.logger import logger
from constants.match_constants import DELAY_IN_S_BEFORE_MATCH_EXCLUSION
from dto.room_dto import RoomDto
from handlers.match_handler_unit import MatchHandlerUnit
from manager import MultiProcessingManager
from utils.models.polling_worker import PollingWorker
from utils.models.sptimer import SPTimer


class MatchHandler:
    """
    Class responsible for monitoring all the pending and ongoing matches between 2 players.
    """

    def __init__(self):
        self.units: dict[str, MatchHandlerUnit] = {}
        self.exit_watchers: dict[str, SPTimer] = {}
        self.lock = MultiProcessingManager.get_lock()
        self.exit_watcher_generation_queue = None
        self.exit_watcher_generator = PollingWorker(
            consumer_method=_initiate_exit_watcher,
            queue=self.exit_watcher_generation_queue,
        )

    def create_exit_watcher(self, player_id: str):
        """
        Registers a player id into the exit watcher generation queue for the generator
        to automatically create an exit watcher.
        """
        manager = MultiProcessingManager.get_instance()
        paused_event = manager.Event()
        stopped_event = manager.Event()

        if self.exit_watcher_generation_queue is None:
            self.exit_watcher_generation_queue = manager.Queue()

        if not self.exit_watcher_generator.started:
            self.exit_watchers = manager.dict()
            self.exit_watcher_generator.arguments_queue = (
                self.exit_watcher_generation_queue
            )
            self.exit_watcher_generator.start()

        self.exit_watcher_generation_queue.put(
            ((paused_event, stopped_event, player_id, self.exit_watchers), {})
        )

    def initiate_match(self, room_dto: RoomDto):
        """
        Instanciates a match handler unit and its corresponding match for a specific room.
        """
        room_id = room_dto.id
        if room_id in self.units:
            raise ValueError(f"The room {room_id} already has an attributed unit")

        match_handler_unit = MatchHandlerUnit(room_dto)

        self.units[room_dto.id] = match_handler_unit
        return match_handler_unit

    def get_unit(self, room_id):
        """
        Gets a unit from the corresponding room id
        """
        try:
            return self.units[room_id]
        except KeyError:
            logger.error(f"No unit instanciated for the room : {room_id}")

    def get_match_info(self, room_id):
        """
        Gets the match info for the corresponding room id
        """
        unit = self.get_unit(room_id)

        if not unit:
            return

        return unit.match_info

    def start_exit_watcher(self, player_id: str, exit_function, exit_function_args):
        with self.lock:
            # logger.debug(f"exit_watchers is {self.exit_watchers}")
            exit_watcher = self.exit_watchers[player_id]
            exit_watcher.on_tick = exit_function
            exit_watcher.on_tick_args = exit_function_args
            exit_watcher.start()

    def stop_exit_watcher(self, player_id: str):
        with self.lock:
            exit_watcher = self.exit_watchers.get(player_id)
            if exit_watcher is not None:
                exit_watcher.stop()

    def remove_exit_watcher(self, player_id: str):
        self.stop_exit_watcher(player_id)
        with self.lock:
            if player_id in self.exit_watchers:
                logger.debug(f"Deleting the exit watcher for the player {player_id}")
                del self.exit_watchers[player_id]


def _initiate_exit_watcher(paused_event, stopped_event, player_id, exit_watchers):
    """
    Creates the exit watcher for a given player (from its id)
    """
    exit_watcher = SPTimer(
        paused_event=paused_event,
        stopped_event=stopped_event,
        tick_interval=DELAY_IN_S_BEFORE_MATCH_EXCLUSION,
        on_tick=None,
        max_ticks=1,
    )
    exit_watchers[player_id] = exit_watcher
    logger.debug(f"Exit watcher initiated for the player {player_id}")
