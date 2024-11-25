from typing import TYPE_CHECKING

from config.logging import get_configured_logger

if TYPE_CHECKING:
    from handlers.match_helpers.match_handler_unit import MatchHandlerUnit


class ServiceBase:
    """
    Base class for all of our services.

    Services are helper classes designed to help the match handler unit
    handle a match by each having their single responsibility.
    """

    def __init__(self, match_handler_unit: "MatchHandlerUnit"):
        self.logger = get_configured_logger(__name__)
        self._server = match_handler_unit.server
        self.match = match_handler_unit
        self.match_info = match_handler_unit.match_info
