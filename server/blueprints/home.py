from flask import Blueprint, session

from constants.session_variables import ROOM_ID
from dto.server_only.home_state_dto import HomeState, HomeStateDto
from handlers import match_handler
from middlewares.error_handler import handle_error


home_bp = Blueprint("home", __name__)
home_bp.register_error_handler(Exception, handle_error)


@home_bp.route("/home-state", methods=["GET"])
def get_home_state():
    room_id = session.get(ROOM_ID)
    if not room_id:
        return HomeStateDto(HomeState.PLAY.value, "", False).to_dict(), 200

    mhu = match_handler.get_unit(room_id)
    if (
        mhu is None or mhu.is_ended()
    ):  # TODO check if the match is ended from either the saved closure or something else TBD
        return (
            HomeStateDto(
                HomeState.PLAY.value,
                "You lost your previous match as you left it.",
                True,
            ).to_dict(),
            200,
        )

    if mhu.is_waiting_to_start() or mhu.is_ongoing():
        return (
            HomeStateDto(
                HomeState.JOIN_BACK.value,
                "You are currently in a match, click the button below to join it back",
                False,
            ).to_dict(),
            200,
        )
