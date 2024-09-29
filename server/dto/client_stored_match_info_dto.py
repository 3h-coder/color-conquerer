from dataclasses import dataclass

from dto.base_dto import BaseDto


@dataclass
class ClientStoredMatchInfoDto(BaseDto):
    playerId: str
    roomId: str
