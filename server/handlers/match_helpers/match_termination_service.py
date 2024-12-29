from config.logging import get_configured_logger
from constants.match_constants import DELAY_IN_S_BEFORE_MATCH_HANDLER_UNIT_DELETION
from dto.partial_match_closure_dto import PartialMatchClosureDto
from dto.server_only.match_closure_dto import EndingReason, MatchClosureDto
from handlers.match_helpers.client_notifications import notify_match_ending
from handlers.match_helpers.match_handler_unit import MatchStatus
from handlers.match_helpers.service_base import ServiceBase

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from handlers.match_helpers.match_handler_unit import MatchHandlerUnit


class MatchTerminationService(ServiceBase):
    """
    Helper class responsible for properly ending/cancelling a match and
    cleaning up all of the associated resources.
    """

    def __init__(self, match_handler_unit: "MatchHandlerUnit"):
        super().__init__(match_handler_unit)
        self._logger = get_configured_logger(__name__)
        # Dto which we use to share/save the final match data before disposing the handler unit
        self.match_closure_info = None

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
            f"Received termination request for the match in the room {self.match_info.roomId}"
        )

        if not self.match.is_ongoing():
            self._logger.warning(
                f"Can only end a match that is ongoing. The match status is {self.match.status.name}"
            )
            return

        self._verify_ids(reason, winner_id, loser_id)

        winner, loser = self._get_winner_and_loser(winner_id, loser_id)

        self.match.status = MatchStatus.ENDED
        self.match_closure_info = MatchClosureDto(reason, winner, loser)

        # TODO: save the match result into a database
        self._logger.debug(f"Match ended -> {self.match_closure_info}")

        self._notify_match_ending()
        self._close_rooms()
        self._schedule_garbage_collection()

    def cancel_match(self):
        """
        Cancels a match, scheduling its garbage collection.

        Typically happens when no player joined, hence why there is no winner/loser
        nor notification sent.
        """
        self._logger.info(
            f"Match cancellation requested for the match in the room {self.match_info.roomId}"
        )

        if not self.match.is_waiting_to_start():
            self._logger.warning(
                f"Can only cancel a match that is waiting to start. The match status is {self.match.status.name}"
            )
            return

        self.match.status = MatchStatus.ABORTED
        self._schedule_garbage_collection()

    def _verify_ids(self, reason, winner_id, loser_id):
        """
        Raises a value error if the provided ids are incorrect.
        """
        if winner_id is None and loser_id is None and reason != EndingReason.DRAW:
            raise ValueError("No winner id nor loser id provided")

        if winner_id == loser_id:
            raise ValueError("The provided winner and loser id values were identical")

    def _get_winner_and_loser(self, winner_id, loser_id):
        player1 = self.match_info.player1
        player2 = self.match_info.player2
        winner = None
        loser = None

        if winner_id is not None:
            winner = self.match.get_player(winner_id)
            loser = player1 if winner == player2 else player2
        else:
            loser = self.match.get_player(loser_id)
            winner = player1 if loser == player2 else player2
        return winner, loser

    def _notify_match_ending(self):
        notify_match_ending(
            PartialMatchClosureDto.from_match_closure_dto(self.match_closure_info),
            self.match_info.roomId,
        )

    def _close_rooms(self):
        self.match.server.socketio.close_room(self.match_info.roomId)

        from handlers import room_handler

        room_handler.remove_closed_room(self.match_info.roomId)

    def _schedule_garbage_collection(self):
        """
        Schedules the deletion of this match handler unit and the associated room.
        """
        self.match.server.socketio.start_background_task(
            target=self._delete_match_and_room
        )

    def _delete_match_and_room(self):
        self.match.server.socketio.sleep(DELAY_IN_S_BEFORE_MATCH_HANDLER_UNIT_DELETION)

        room_id = self.match_info.roomId
        self._logger.debug(f"Deleting the match handler unit for the room {room_id}")

        from handlers import match_handler, room_handler

        if room_id in room_handler.closed_rooms:
            room_handler.remove_closed_room(room_id)

        if room_id not in match_handler.units:
            self._logger.warning(
                f"Tried to delete a match handler unit that did not exist : {room_id}"
            )
            return

        del match_handler.units[room_id]
