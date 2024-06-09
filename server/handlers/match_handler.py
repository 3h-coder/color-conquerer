from handlers.match_handler_unit import MatchHandlerUnit


class MatchHandler:
    """
    Class responsible for monitoring a match between
    2 players.
    """

    def __init__(self):
        self.units: dict[str, MatchHandlerUnit] = {}

    def get_unit(self, unit_id):
        try:
            return self.units[unit_id]
        except KeyError:
            return None
