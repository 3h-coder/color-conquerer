from dataclasses import dataclass

from game_engine.models.match.cancellation_reason import CancellationReason
from game_engine.models.player.player import Player


@dataclass
class MatchCancellationInfo:
    cancellation_reason: CancellationReason
    penalized_player: Player | None
