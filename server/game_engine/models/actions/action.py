from dto.coordinates_dto import CoordinatesDto
from game_engine.models.match_context import MatchContext


class Action:
    """
    Base class for all actions
    """

    DEFAULT_MANA_COST = 0

    def __init__(
        self,
        from_player1: bool,
        impacted_coords: CoordinatesDto,
    ):
        self.from_player1 = from_player1
        self.impacted_coords = impacted_coords
        self.mana_cost = self.DEFAULT_MANA_COST

    def __repr__(self):
        return (
            f"<Action(from_player1={self.from_player1}, "
            f"impacted_coords={self.impacted_coords}, "
            f"mana_cost={self.mana_cost})>"
        )

    def to_dto(self):
        raise NotImplementedError

    @staticmethod
    def create(*args, **kwargs) -> "Action":
        raise NotImplementedError

    @staticmethod
    def calculate(*args, **kwargs) -> set["Action"]:
        """
        Returns a list of instances of the class based on the given parameters.
        """
        raise NotImplementedError

    def apply(self, match_context: MatchContext):
        """
        Applies the action on the given board.
        """
        raise NotImplementedError
