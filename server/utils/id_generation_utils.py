import uuid
from enum import StrEnum

from dto.player.queue_player_dto import QueuePlayerDto
from dto.player.user_dto import UserDto
from game_engine.models.cell.cell import Cell
from game_engine.models.match_context import MatchContext
from game_engine.models.room import Room


class IdPrefixes(StrEnum):
    USER = "u"
    PLAYER = "p"
    ROOM = "r"
    MATCH = "m"
    CELL = "c"


def generate_id(type):
    if type is UserDto:
        return f"{IdPrefixes.USER}-{uuid.uuid4()}"
    elif type is QueuePlayerDto:
        return f"{IdPrefixes.PLAYER}-{uuid.uuid4()}"
    elif type is Room:
        return f"{IdPrefixes.ROOM}-{uuid.uuid4()}"
    elif type is MatchContext:
        return f"{IdPrefixes.MATCH}-{uuid.uuid4()}"
    elif type is Cell:
        return f"{IdPrefixes.CELL}-{uuid.uuid4()}"
