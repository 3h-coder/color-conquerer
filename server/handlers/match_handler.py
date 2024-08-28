import multiprocessing

from config.config import logger
from constants.match_constants import DELAY_IN_S_BEFORE_MATCH_EXCLUSION
from dto.room_dto import RoomDto
from handlers.match_handler_unit import MatchHandlerUnit
from manager import MultiProcessingManager
from utils.models.polling_worker import PollingWorker
from utils.models.sptimer import SPTimer


class MatchHandler:
    """
    Class responsible for monitoring all the ongoing matches between 2 players.
    """

    def __init__(self):
        self.units: dict[str, MatchHandlerUnit] = {}
        self.exit_watchers: dict[str, SPTimer] = {}
        self.exit_watcher_generation_queue = multiprocessing.Queue()
        self.exit_watcher_generator = PollingWorker(
            queue=self.exit_watcher_generation_queue,
            consumer_method=_initiate_exit_watcher,
        )

    def _init_exit_watchers(self):
        shared_dict, shared_lock = MultiProcessingManager.get_shared_dict_and_lock()
        with shared_lock:
            shared_dict["exit_watchers"] = {}
            return shared_dict["exit_watchers"]

    def create_exit_watcher(self, player_id: str):
        """
        Registers a player id into the exit watcher generation queue for the generator
        to automatically create an exit watcher.
        """
        if not self.exit_watcher_generator.started:
            self.exit_watchers = self._init_exit_watchers()
            self.exit_watcher_generator.start()
        self.exit_watcher_generation_queue.put(((player_id, self.exit_watchers), {}))

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
        # TODO : [BUG] The exit watcher must already exist at this point. Creating it takes a bit of time,
        # more time than a page refresh actually which triggers a key error when trying to stop it.

        exit_watcher = self.exit_watchers[player_id]
        exit_watcher.on_tick = exit_function
        exit_watcher.on_tick_args = exit_function_args
        exit_watcher.start()

    def stop_exit_watcher(self, player_id: str):
        exit_watcher = self.exit_watchers[player_id]
        exit_watcher.stop()


def _initiate_exit_watcher(player_id, exit_watchers):
    """
    Creates the exit watcher for a given player (from its id)
    """
    exit_watcher = SPTimer(
        MultiProcessingManager.get_instance(),
        tick_interval=DELAY_IN_S_BEFORE_MATCH_EXCLUSION,
        on_tick=None,
        max_ticks=1,
    )
    exit_watchers[player_id] = exit_watcher
    logger.debug(f"Exit watcher initiated for the player {player_id}")
