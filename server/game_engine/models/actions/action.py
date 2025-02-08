from dataclasses import dataclass

from dto.coordinates_dto import CoordinatesDto
from game_engine.models.cell.cell import Cell


@dataclass
class Action:
    """
    Base class for all actions
    """

    from_player1: bool
    is_direct: bool
    impacted_coords: CoordinatesDto
    mana_cost: int

    @classmethod
    def calculate(cls):
        """
        Returns a list of instances of the class based on the given parameters.
        """
        raise NotImplementedError

    def process(self, board: list[list[Cell]]):
        """
        Applies the action on the given board.
        """
        raise NotImplementedError
