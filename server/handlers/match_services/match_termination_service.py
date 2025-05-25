from typing import TYPE_CHECKING

from constants.match_constants import DELAY_IN_S_BEFORE_MATCH_AND_CLOSED_ROOM_DELETION
from game_engine.models.match.cancellation_reason import CancellationReason
from game_engine.models.match.match_cancellation_info import MatchCancellationInfo
from game_engine.models.match.match_closure_info import EndingReason, MatchClosureInfo
from handlers.match_services.client_notifications import (
    notify_match_cancelled,
    notify_match_ending,
)
from handlers.match_services.service_base import ServiceBase
from persistence.database import db
from persistence.database.models.ended_match import EndedMatch

if TYPE_CHECKING:
    from handlers.match_handler_unit import MatchHandlerUnit


class MatchTerminationService(ServiceBase):
    """
    Helper class responsible for properly ending/cancelling a match and
    cleaning up all of the associated resources.
    """

    def __init__(self, match_handler_unit: "MatchHandlerUnit"):
        super().__init__(match_handler_unit)
        self._logger = match_handler_unit.logger
        # Data objects which we use to share/save the final match data before disposing the handler unit
        # Note : both objects should never be populated at the same time
        self.match_closure_info: MatchClosureInfo | None = None
        self.match_cancellation_info: MatchCancellationInfo | None = None

    def end_match(
        self,
        reason: EndingReason,
        winner_id: str | None = None,
        loser_id: str | None = None,
    ):
        """
        Declares the match as ended, registering the information in a
        dedicated database and removing the room from the room handler.

        Additionally, notifies all players and schedules this match handler unit's garbage collection.
        """
        self._logger.info(
            f"Received termination request for the match in the room {self.match_context.room_id}, "
            f"the termination request reason is {reason.name}"
        )

        if not self.match.is_ongoing():
            self._logger.warning(
                f"Can only end a match that is ongoing. The match status is {self.match.status.name}"
            )
            return

        self._verify_ids(reason, winner_id, loser_id)

        winner, loser = self._get_winner_and_loser(winner_id, loser_id)

        self.match.mark_as_ended()

        self.match_closure_info = MatchClosureInfo(
            ending_reason=reason,
            winner=winner,
            loser=loser,
            total_turns=self.match_context.current_turn,
            actions_per_turn_serialized=self.match.get_actions_per_turn(
                serialized=True
            ),
        )
        self._logger.debug(f"Match ended -> {self.match_closure_info.simple_str()}")

        self._save_ended_match_into_database()

        self._notify_match_ending()

        self._close_room()
        self._schedule_garbage_collection()

    def cancel_match(
        self, cancellation_reason: CancellationReason, penalized_player_id: str = ""
    ):
        """
        Cancels a match, scheduling its garbage collection.

        Typically happens when no player joined, hence why there is no winner/loser
        nor notification sent.
        """
        self._logger.info(
            f"Match cancellation requested for the match in the room {self.match_context.room_id}. The reason is {cancellation_reason.name}."
        )

        if not self.match.is_waiting_to_start():
            self._logger.warning(
                f"Can only cancel a match that is waiting to start. The match status is {self.match.status.name}"
            )
            return

        self.match.mark_as_cancelled()

        # TODO: save the match cancellation somewhere
        other_player, penalized_player = self._get_winner_and_loser(
            None, penalized_player_id
        )
        self.match_cancellation_info = MatchCancellationInfo(
            cancellation_reason=cancellation_reason, penalized_player=penalized_player
        )
        notify_match_cancelled(
            player_room=other_player.individual_room_id,
            message="Your opponent did not join the match",
        )

        self._schedule_garbage_collection()

    def _verify_ids(self, reason, winner_id, loser_id):
        """
        Raises a value error if the provided ids are incorrect.
        """
        if winner_id is None and loser_id is None and reason != EndingReason.DRAW:
            raise ValueError("No winner id nor loser id provided")

        if winner_id == loser_id and winner_id is not None:
            raise ValueError("The provided winner and loser id values were identical")

    def _get_winner_and_loser(self, winner_id: str, loser_id: str):
        player1 = self.match_context.player1
        player2 = self.match_context.player2
        winner = None
        loser = None

        if winner_id is not None:
            winner = self.match.get_player(winner_id)
            loser = player1 if winner == player2 else player2
        elif loser_id is not None:
            loser = self.match.get_player(loser_id)
            winner = player1 if loser == player2 else player2
        return winner, loser

    def _notify_match_ending(self):
        notify_match_ending(
            self.match_closure_info.to_dto(),
            self.match_context.room_id,
        )

    def _close_room(self):
        self.match.server.socketio.close_room(self.match_context.room_id)

    def _schedule_garbage_collection(self):
        """
        Schedules the deletion of this match handler unit and the associated room.
        """
        self.match.server.socketio.start_background_task(
            target=self._delete_match_and_room
        )

    def _delete_match_and_room(self):
        self.match.server.socketio.sleep(
            DELAY_IN_S_BEFORE_MATCH_AND_CLOSED_ROOM_DELETION
        )

        room_id = self.match_context.room_id
        self._logger.debug(f"Deleting the match handler unit for the room {room_id}")

        room_handler = self._server.room_handler
        match_handler = self._server.match_handler

        if room_id in room_handler.closed_rooms:
            room_handler.remove_closed_room(room_id)

        if room_id not in match_handler.units:
            self._logger.warning(
                f"Tried to delete a match handler unit that did not exist : {room_id}"
            )
            return

        del match_handler.units[room_id]

    def _save_ended_match_into_database(self):
        """
        Saves the ended match information into the database.
        Does nothing if the server is in testing mode.
        """
        if self.match.server.testing:
            return

        try:
            ended_match = EndedMatch.from_closure_info(self.match_closure_info)
            db.session.add(ended_match)
            db.session.commit()
        except Exception as ex:
            self._logger.error(
                f"Failed to save the ended match into the database: {ex}"
            )
            db.session.rollback()
