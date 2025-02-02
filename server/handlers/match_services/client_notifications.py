from typing import TYPE_CHECKING

from flask_socketio import emit

from dto.message_dto import MessageDto
from dto.partial_match_closure_dto import PartialMatchClosureDto
from dto.possible_actions_dto import PossibleActionsDto
from dto.processed_action_dto import ProcessedActionDto
from dto.turn_info_dto import TurnInfoDto
from events.events import Events
from server_gate import get_server

if TYPE_CHECKING:
    from server import Server

_server: "Server" = None


def notify_match_start(turn_info: TurnInfoDto, room_id: str):
    _emit(Events.SERVER_MATCH_START, turn_info.to_dict(), to=room_id)


def notify_turn_swap(turn_info: TurnInfoDto, room_id: str):
    _emit(Events.SERVER_TURN_SWAP, turn_info.to_dict(), to=room_id)


def notify_possible_actions(possible_actions: PossibleActionsDto):
    emit(Events.SERVER_POSSIBLE_ACTIONS, possible_actions.to_dict())


def notify_processed_action(processed_actions: ProcessedActionDto, room_id: str):
    _emit(Events.SERVER_PROCESSED_ACTIONS, processed_actions.to_dict(), to=room_id)


def notify_action_error(error_msg: str):
    emit(Events.SERVER_ACTION_ERROR, MessageDto(error_msg).to_dict())


def notify_match_ending(match_closure_info: PartialMatchClosureDto, room_id: str):
    _emit(Events.SERVER_MATCH_END, match_closure_info.to_dict(), to=room_id)


def _emit(*args, **kwargs):
    _ensure_server_is_set()
    _server.socketio.emit(*args, **kwargs)


def _ensure_server_is_set():
    global _server

    if _server is None:
        _server = get_server()
