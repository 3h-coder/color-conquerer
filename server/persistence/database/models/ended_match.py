from datetime import datetime

from sqlalchemy import JSON, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from game_engine.models.match.match_closure_info import MatchClosureInfo
from persistence.database import db
from persistence.database.tables import Table


class EndedMatch(db.Model):
    """
    Represents an ended match in the database.
    """

    __tablename__ = Table.ENDED_MATCHES

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    winner_user_id: Mapped[str | None] = mapped_column(String(256), nullable=True)
    loser_user_id: Mapped[str | None] = mapped_column(String(256), nullable=True)
    ending_reason: Mapped[str] = mapped_column(String(256), nullable=False)
    total_turns: Mapped[int] = mapped_column(Integer, nullable=False)
    actions_per_turn: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    ended_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    def __repr__(self):
        return f"<EndedMatch {self.id} - {self.winner_user_id} vs {self.loser_user_id}>"

    @staticmethod
    def from_closure_info(closure_info: MatchClosureInfo):
        """
        Create an EndedMatch instance from a MatchClosureInfo object.
        """
        return EndedMatch(
            winner_user_id=closure_info.winner.user_id if closure_info.winner else None,
            loser_user_id=closure_info.loser.user_id if closure_info.loser else None,
            ending_reason=closure_info.ending_reason.value,
            total_turns=closure_info.total_turns,
            actions_per_turn=closure_info.actions_per_turn_serialized,
        )

    def __repr__(self):
        return f"<EndedMatch {self.id} - {self.winner_user_id} vs {self.loser_user_id}>"
