from dataclasses import dataclass
from enum import IntEnum

from dto.match.match_closure_dto import MatchClosureDto
from game_engine.models.player import Player


class EndingReason(IntEnum):
    PLAYER_VICTORY = 1
    DRAW = 2
    PLAYER_CONCEDED = 3
    PLAYER_LEFT = 4
    PLAYER_INACTIVE = 5
    NEVER_JOINED = 6
    # When the player dies from damage due to low stamina
    FATIGUE = 7


@dataclass
class MatchClosure:
    endingReason: EndingReason
    winner: Player | None  # None if draw or no winner
    loser: Player | None  # None if draw or no loser
    totalTurns: int
    actionsPerTurn: dict[int, list]

    def simple_str(self) -> str:
        """
        Returns a simple string representation of the match closure information containing the ending reason, winner, loser, and total turns.
        """
        return f"MatchClosureDto(endingReason={self.endingReason}, winner={self.winner}, loser={self.loser}, totalTurns={self.totalTurns})"

    def to_dto(self):
        winner_dto = self.winner.to_dto() if self.winner else None
        loser_dto = self.loser.to_dto() if self.loser else None
        return MatchClosureDto(
            endingReason=self.endingReason,
            winner=winner_dto,
            loser=loser_dto,
        )
