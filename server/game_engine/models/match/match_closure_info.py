from dataclasses import dataclass

from dto.match.match_closure_dto import MatchClosureDto
from game_engine.models.match.ending_reason import EndingReason
from game_engine.models.player.player import Player


@dataclass
class MatchClosureInfo:
    ending_reason: EndingReason
    winner: Player | None  # None if draw or no winner
    loser: Player | None  # None if draw or no loser
    total_turns: int
    actions_per_turn_serialized: dict[int, list[dict]]

    def simple_str(self) -> str:
        """
        Returns a simple string representation of the match closure information containing the ending reason, winner, loser, and total turns.
        """
        return f"MatchClosureDto(endingReason={self.ending_reason}, winner={self.winner}, loser={self.loser}, totalTurns={self.total_turns})"

    def to_dto(self):
        winner_dto = self.winner.to_dto() if self.winner else None
        loser_dto = self.loser.to_dto() if self.loser else None
        return MatchClosureDto(
            endingReason=self.ending_reason,
            winner=winner_dto,
            loser=loser_dto,
        )
