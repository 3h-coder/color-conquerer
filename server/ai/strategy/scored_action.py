from dataclasses import dataclass
from typing import Any


@dataclass
class ScoredAction:
    """
    Pairs an action with its evaluated score so different action types
    can compete on a unified scale inside the decision brain.
    """

    action: Any
    score: float
