from typing import TYPE_CHECKING

from dto.partial_match_closure_dto import PartialMatchClosureDto
from dto.turn_info_dto import TurnInfoDto
from events.events import Events
from server_gate import get_server

if TYPE_CHECKING:
    from server import Server

_server: "Server" = None


def notify_match_start(turn_info: TurnInfoDto, room_id: str):
    _emit(Events.SERVER_MATCH_START.value, turn_info.to_dict(), to=room_id)


def notify_turn_swap(turn_info: TurnInfoDto, room_id: str):
    _emit(Events.SERVER_TURN_SWAP.value, turn_info.to_dict(), to=room_id)


def notify_match_end(match_closure_info: PartialMatchClosureDto, room_id: str):
    _emit(Events.SERVER_MATCH_END.value, match_closure_info.to_dict(), to=room_id)


def _emit(*args, **kwargs):
    _ensure_server_is_set()
    _server.socketio.emit(*args, **kwargs)


def _ensure_server_is_set():
    global _server

    if _server is None:
        _server = get_server()
