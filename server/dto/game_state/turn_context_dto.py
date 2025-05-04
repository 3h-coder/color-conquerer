from dataclasses import dataclass

from dto.base_dto import BaseDto
from dto.game_state.game_context_dto import GameContextDto
from dto.game_state.turn_processing_result_dto import TurnProcessingResultDto


@dataclass
class TurnContextDto(BaseDto):
    """
    Contains information about the current turn context.
    Note : A turn context is meant to be sent to a single client,
    as it contains information that the other client should not be aware of.
    """

    currentPlayerId: str
    isPlayer1Turn: bool
    remainingTimeInS: int
    durationInS: int
    notifyTurnChange: bool
    gameContext: GameContextDto
    # None if not for a turn change
    newTurnProcessingInfo: TurnProcessingResultDto | None = None
