from flask import Blueprint, current_app, session

from dto.game_state.home_state_dto import HomeState, HomeStateDto
from middlewares.error_handler import handle_error
from server_gate import get_match_handler
from session_management import session_utils
from session_management.session_variables import IN_MATCH, ROOM_ID

home_bp = Blueprint("home", __name__)
home_bp.register_error_handler(Exception, handle_error)


@home_bp.route("/home-state", methods=["GET"])
def get_home_state():
    """
    This endpoint should be requested by the client each time they navigate to the home page.

    It verifies the consistency of the player's session variables as well as checking if the player
    should rejoin a match, or be notified that they lost their previous match due to leaving.
    """
    room_id = session.get(ROOM_ID)
    in_match = session.get(IN_MATCH)

    if not room_id and not in_match:
        return _default_homestate_response()

    if room_id and not in_match:
        # Most likely an error at match creation/start, and the session was not properly cleared from disconnecting
        current_app.logger.warning(
            "ROOM_ID is set yet IN_MATCH is not, resetting the player's session"
        )
        session_utils.clear_match_info()
        return _default_homestate_response()

    if not room_id and in_match:
        # Should never happen but just in case
        current_app.logger.warning(
            "ROOM_ID is not set yet IN_MATCH is set, resetting the player's session"
        )
        session_utils.clear_match_info()
        return _default_homestate_response()

    match_handler = get_match_handler()
    match = match_handler.get_unit(room_id)

    # TODO : make this more reliable -> Check on ended matches (in memory ? in database ?)
    if match is None or match.is_ended():
        session_utils.clear_match_info()
        return (
            HomeStateDto(
                HomeState.PLAY,
                "You lost your previous match as you left it.",
            ).to_dict(),
            200,
        )

    elif match.is_waiting_to_start() or match.is_ongoing():
        return (
            HomeStateDto(
                HomeState.JOIN_BACK,
                "You are currently in a match, click the button below to join it back",
            ).to_dict(),
            200,
        )

    elif match.is_cancelled():
        session_utils.clear_match_info()
        return _default_homestate_response()


def _default_homestate_response():
    return HomeStateDto(HomeState.PLAY, "").to_dict(), 200
