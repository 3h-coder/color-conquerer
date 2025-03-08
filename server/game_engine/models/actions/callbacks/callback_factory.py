from typing import TYPE_CHECKING

from game_engine.models.actions.callbacks.action_callback_id import ActionCallBackId

if TYPE_CHECKING:
    from game_engine.models.actions.action import Action
    from game_engine.models.actions.callbacks.action_callback import ActionCallback


def get_callback(
    id: ActionCallBackId,
    parent_action: "Action",
    parent_callback: "ActionCallback" = None,
) -> "ActionCallback":
    """
    Factory method to create a callback based on the given id.
    """
    from game_engine.models.actions.callbacks.mine_explosion_callback import (
        MineExplosionCallback,
    )

    CALLBACKS = {
        ActionCallBackId.MINE_EXPLOSION: lambda parent_action, parent_callback: MineExplosionCallback(
            parent_action, parent_callback
        )
    }

    return CALLBACKS[id](parent_action, parent_callback)
