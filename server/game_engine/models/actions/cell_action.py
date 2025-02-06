from dataclasses import dataclass

from dto.coordinates_dto import CoordinatesDto
from game_engine.models.actions.action import Action


@dataclass
class CellAction(Action):
    originating_coords: CoordinatesDto
    cell_id: str
