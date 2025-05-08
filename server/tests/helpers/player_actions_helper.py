from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tests.helpers.match_helper import MatchHelper


class PlayerActionsHelper:
    """
    Helper class to perform certain actions in a more straightworward way.
    """

    def __init__(self, match: "MatchHelper"):
        self.match = match
        self.clients = match.get_clients()
