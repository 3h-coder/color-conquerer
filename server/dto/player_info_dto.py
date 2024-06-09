from dataclasses import dataclass

from dto.base_dto import BaseDto
from dto.cell_info_dto import CellInfoDto
from dto.user_dto import UserDto


@dataclass
class PlayerInfoDto(BaseDto):
    user: UserDto
    playerId: str
    controlledCells: list[CellInfoDto]
