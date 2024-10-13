import uuid
from enum import Enum

from dto.partial_match_info_dto import PartialMatchInfoDto
from dto.server_only.match_info_dto import MatchInfoDto
from dto.queue_player_dto import QueuePlayerDto
from dto.server_only.room_dto import RoomDto
from dto.user_dto import UserDto


class IdPrefixes(Enum):
    USER = "u"
    PLAYER = "p"
    ROOM = "r"
    MATCH = "m"


def generate_id(type):
    if type is UserDto:
        return f"{IdPrefixes.USER.value}-{uuid.uuid4()}"
    elif type is QueuePlayerDto:
        return f"{IdPrefixes.PLAYER.value}-{uuid.uuid4()}"
    elif type is RoomDto:
        return f"{IdPrefixes.ROOM.value}-{uuid.uuid4()}"
    elif type is MatchInfoDto or type is PartialMatchInfoDto:
        return f"{IdPrefixes.MATCH.value}-{uuid.uuid4()}"
