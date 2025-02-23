from dataclasses import dataclass
from typing import Iterable

from dto.action_callback_dto import ActionCallbackDto
from dto.base_dto import BaseDto
from game_engine.models.actions.callbacks.action_callback import ActionCallback


@dataclass
class ActionCallbacksDto(BaseDto):
    callbacks: list[ActionCallbackDto]

    @staticmethod
    def from_callbacks(callbacks: Iterable[ActionCallback], for_player1: bool):
        callbacks = [callback.to_dto(for_player1) for callback in callbacks]
        return ActionCallbacksDto(callbacks)
