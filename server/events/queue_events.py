from flask import session
from flask_socketio import emit, join_room, leave_room

from config.logger import logger
from dto.match_info_dto import MatchInfoDto
from dto.queue_player_dto import QueuePlayerDto
from events.events import Events
from exceptions.queue_error import QueueError
from handlers import match_handler, room_handler
from helpers.id_generation_helper import generate_id


def handle_queue_registration(data: dict):
    """
    Handles match making requests, starting with the queue-register event.

    Is in charge of creating the room up to creating the match.
    """
    try:
        if room_handler.at_capacity():
            logger.info("Room handler at maximum capacity, denying queue registration")
            emit(Events.SERVER_QUEUE_FULL.value)
            return

        queue_player_dto = QueuePlayerDto.from_dict(data)
        player_id = set_player_id(queue_player_dto)

        logger.info(
            f"{Events.SERVER_QUEUE_REGISTERED.name} event : {queue_player_dto.playerId}"
        )

        (room_id, closed) = make_enter_in_room(queue_player_dto)

        # The room in which the player entered already had a player waiting.
        # In that case, initiate the match, and notify both clients that an opponent was found.
        if closed:
            match_info = match_handler.initiate_match(
                room_handler.closed_rooms[room_id]
            ).match_info
            # save the player info in the session
            set_player_info(player_id, match_info)
            emit(Events.SERVER_QUEUE_OPPONENT_FOUND.value, to=room_id, broadcast=True)

    except Exception as ex:
        logger.error(f"An error occured during a match finding request : {ex}")
        raise QueueError(ex)


def handle_queue_withdrawal(data: dict):
    """
    Handles the queue-withdrawal event.
    """
    try:
        queue_register_dto = QueuePlayerDto.from_dict(data)
        logger.info(
            f"{Events.CLIENT_QUEUE_WITHDRAWAL.name} event : {queue_register_dto.playerId}"
        )

        room_id = session["room_id"]
        leave_room(room_id)

        # Technically, only open rooms allow queue-withdrawal,
        # leaving a closed room automatically leads to match ending
        room_handler.remove_room(room_id)

    except Exception as ex:
        logger.error(f"An error occured during queue withdrawal : {ex}")
        raise QueueError()


def set_player_id(queue_player_dto: QueuePlayerDto):
    """
    Sets the player id and saves it into the session.
    """
    player_id = generate_id(QueuePlayerDto)
    queue_player_dto.playerId = player_id

    return player_id


def make_enter_in_room(queue_player_dto: QueuePlayerDto):
    """
    Set the session's room id and notifies the client that the player is registered in a room.
    """
    (room_id, closed) = room_handler.make_enter_in_room(queue_player_dto)

    session["room_id"] = room_id
    join_room(room_id)

    emit(
        Events.SERVER_QUEUE_REGISTERED.value
    )  # Notify the client that registration succeeded

    return room_id, closed


def set_player_info(player_id: str, match_info: MatchInfoDto):
    """
    Saves the player information into the session.
    """
    player_info = (
        match_info.player1
        if match_info.player1.playerId == player_id
        else match_info.player2
    )
    session["player_info"] = player_info
