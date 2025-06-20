from dataclasses import dataclass

from dto.game_state.turn_processing_result_dto import TurnProcessingResultDto
from game_engine.models.match.match_closure_info import EndingReason


@dataclass
class TurnProcessingResult:
    """
    Represents the result of processing a turn in the game engine.
    """

    # Applicable if a turn change triggered a match end
    # (e.g., player lost due to fatigue)
    match_ending_reason: EndingReason | None
    # The fatigue damage that the current player has received after the turn change
    ongoing_fatigue_damage: int

    @staticmethod
    def get_default():
        return TurnProcessingResult(
            match_ending_reason=None,
            ongoing_fatigue_damage=0,
        )

    def to_dto(self):
        return TurnProcessingResultDto(fatigueDamage=self.ongoing_fatigue_damage)
