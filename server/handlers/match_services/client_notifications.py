from threading import Lock
from typing import TYPE_CHECKING

from flask_socketio import emit

from dto.actions.action_callback_dto import ActionCallbackDto
from dto.actions.possible_actions_dto import PossibleActionsDto
from dto.actions.processed_action_dto import ProcessedActionDto
from dto.game_state.turn_context_dto import TurnContextDto
from dto.match.partial_match_closure_dto import PartialMatchClosureDto
from dto.misc.message_dto import MessageDto
from events.events import Events
from server_gate import get_server

if TYPE_CHECKING:
    from server import Server

_server: "Server" = None


def notify_match_start(
    turn_context_1: TurnContextDto,
    turn_context_2: TurnContextDto,
    player1_room: str,
    player2_room: str,
    lock: Lock,
):
    with lock:
        _emit(Events.SERVER_MATCH_START, turn_context_1.to_dict(), to=player1_room)
        _emit(Events.SERVER_MATCH_START, turn_context_2.to_dict(), to=player2_room)


def notify_turn_swap(
    turn_context_1: TurnContextDto,
    turn_context_2: TurnContextDto,
    player1_room: str,
    player2_room: str,
    lock: Lock,
):
    with lock:
        _emit(Events.SERVER_TURN_SWAP, turn_context_1.to_dict(), to=player1_room)
        _emit(Events.SERVER_TURN_SWAP, turn_context_2.to_dict(), to=player2_room)


def notify_inactivity_warning(player_room: str):
    _emit(Events.SERVER_INACTIVITY_WARNING, to=player_room)


def notify_possible_actions(possible_actions: PossibleActionsDto):
    emit(Events.SERVER_POSSIBLE_ACTIONS, possible_actions.to_dict())


def notify_processed_action(
    processed_actions_1: ProcessedActionDto,
    processed_actions_2: ProcessedActionDto,
    player1_room: str,
    player2_room: str,
    lock: Lock,
):
    with lock:
        _emit(
            Events.SERVER_PROCESSED_ACTIONS,
            processed_actions_1.to_dict(),
            to=player1_room,
        )
        _emit(
            Events.SERVER_PROCESSED_ACTIONS,
            processed_actions_2.to_dict(),
            to=player2_room,
        )


def notify_triggered_callback(
    action_callback_dto1: ActionCallbackDto,
    action_callback_dto2: ActionCallbackDto,
    player1_room: str,
    player2_room: str,
    lock: Lock,
):
    with lock:
        _emit(
            Events.SERVER_ACTION_CALLBACK,
            action_callback_dto1.to_dict(),
            to=player1_room,
        )
        _emit(
            Events.SERVER_ACTION_CALLBACK,
            action_callback_dto2.to_dict(),
            to=player2_room,
        )


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
