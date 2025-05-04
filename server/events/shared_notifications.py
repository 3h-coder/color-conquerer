"""Socket server side notifications that are shared across the solution"""

from flask_socketio import emit

from dto.misc.message_dto import MessageDto
from events.events import Events


def match_launch_error_redirect(broadcast_to: str | None = None):
    """
    Will order the client to navigate to the home page, and let the player know
    that an error occured while trying to join their match.
    """
    emit(
        Events.SERVER_HOME_ERROR_REDIRECT,
        MessageDto(
            "An error occured while joining your match, please try again"
        ).to_dict(),
        broadcast=bool(broadcast_to),
        to=broadcast_to,
    )
