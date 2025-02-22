from typing import TYPE_CHECKING

from game_engine.models.actions.callbacks.action_callback_id import ActionCallBackId
from game_engine.models.actions.callbacks.mine_explosion_callback import (
    MineExplosionCallback,
)

if TYPE_CHECKING:
    from game_engine.models.actions.action import Action

_CALLBACKS = {
    ActionCallBackId.MINE_EXPLOSION: lambda parent_action: MineExplosionCallback(
        parent_action
    )
}


def get_callback(id: ActionCallBackId, parent_action: "Action"):
    return _CALLBACKS[id](parent_action)
