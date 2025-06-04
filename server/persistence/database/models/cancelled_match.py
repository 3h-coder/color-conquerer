from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from game_engine.models.match.match_cancellation_info import \
    MatchCancellationInfo
from persistence.database import db
from persistence.database.tables import Table


class CancelledMatch(db.Model):
    """
    Represents a cancelled match in the database.
    """

    __tablename__ = Table.CANCELLED_MATCHES

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    penalized_user_id: Mapped[str | None] = mapped_column(String(256), nullable=True)
    reason: Mapped[str] = mapped_column(String(256), nullable=False)
    cancelled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    def __repr__(self):
        return f"<CancelledMatch {self.id} - User: {self.penalized_user_id}, Reason: {self.reason}>"

    @staticmethod
    def from_cancellation_info(cancellation_info: MatchCancellationInfo):
        """
        Create a CancelledMatch instance from a cancellation info object.
        """
        return CancelledMatch(
            penalized_user_id=(
                cancellation_info.penalized_player.user_id
                if cancellation_info.penalized_player
                else None
            ),
            reason=cancellation_info.cancellation_reason.value,
        )
