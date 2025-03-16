from game_engine.models.actions.hooks.action_hook import ActionHook


class ManaBubbleHook(ActionHook):
    """
    Increases the player's mana points by 1 if the action targets a mana bubble cell.
    """

    def trigger(self, action, match_context):
        game_board = match_context.game_board
        target_coords = next(iter(action.impacted_coords))
        target_cell = game_board.get(target_coords.rowIndex, target_coords.columnIndex)

        if not target_cell.is_mana_bubble():
            return

        player_resources = match_context.get_player_resources(action.from_player1)
        player_resources.current_mp = min(
            player_resources.max_mp, player_resources.current_mp + 1
        )
