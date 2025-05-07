from game_engine.models.match.match_context import MatchContext


class MatchContextHelper:
    """
    Helper class that wraps a match context to add custom functionality for tests.
    """

    def __init__(self, match_context: MatchContext):
        self._match_context = match_context
        self._game_board = match_context.game_board

    # region Getters

    def get_current_turn(self):
        return self._match_context.current_turn

    def get_current_player(self):
        return self._match_context.get_current_player()

    def get_both_players_resources(self):
        return self._match_context.get_both_players_resources()

    def get_both_player_match_data(self):
        player1_match_data = self._match_context.player1.match_data
        player2_match_data = self._match_context.player2.match_data
        return (player1_match_data, player2_match_data)

    def get_master_cell(self, of_player_1: bool):
        player_cells = self._game_board.get_cells_owned_by_player(of_player_1)
        return next((cell for cell in player_cells if cell.is_master), None)

    def get_neighbours(self, row_index: int, col_index: int):
        return self._game_board.get_neighbours(row_index, col_index)

    def get_cell_at(self, row_index: int, col_index: int):
        return self._game_board.get(row_index, col_index)

    # endregion
