from flask import Blueprint, session

from constants.session_variables import IN_MATCH, ROOM_ID
from dto.home_state_dto import HomeState, HomeStateDto
from middlewares.error_handler import handle_error
from server_gate import get_match_handler

home_bp = Blueprint("home", __name__)
home_bp.register_error_handler(Exception, handle_error)


@home_bp.route("/home-state", methods=["GET"])
def get_home_state():
    room_id = session.get(ROOM_ID)
    in_match = session.get(IN_MATCH)
    if not room_id or not in_match:
        return HomeStateDto(HomeState.PLAY, "", False).to_dict(), 200

    match_handler = get_match_handler()

    match = match_handler.get_unit(room_id)
    if (
        match is None or match.is_ended()
    ):  # TODO check if the match is ended from either the saved closure or something else TBD
        return (
            HomeStateDto(
                HomeState.PLAY,
                "You lost your previous match as you left it.",
                True,
            ).to_dict(),
            200,
        )

    if match.is_waiting_to_start() or match.is_ongoing():
        return (
            HomeStateDto(
                HomeState.JOIN_BACK,
                "You are currently in a match, click the button below to join it back",
                False,
            ).to_dict(),
            200,
        )
