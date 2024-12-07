from enum import IntEnum
from typing import TYPE_CHECKING
from dto.cell_info_dto import CellInfoDto
from handlers.match_helpers.service_base import ServiceBase

if TYPE_CHECKING:
    from handlers.match_helpers.match_handler_unit import MatchHandlerUnit


class MatchActionsService(ServiceBase):
    """
    Helper class responsible for handling action requests from each players.
    The class handles both the action validation and action processing.
    """

    def __init__(self, match_handler_unit: "MatchHandlerUnit"):
        super().__init__(match_handler_unit)
        # Dictionary storing all of the actions that happened during a match.
        # Key : turn number | Value : list of actions (type : [TBD])
        self.actions: dict[int, list] = {}
        self._turn_actions = (
            []
        )  # used to track all the actions performed during the turn
        self._possible_actions: set = (
            None  # Used to confirm whether an action can be done or not
        )

    def get_possible_actions(cell_info_dto: CellInfoDto):
        """
        Gets all the actions that the player can perform on a cell.
        """
