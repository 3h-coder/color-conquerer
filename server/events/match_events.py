from flask import session
from flask_socketio import emit

from config.config import logger
from events.events import Events
from handlers import match_handler, room_handler


def handle_action_request():
    """
    Handles action request sent by a player.
    Peforms validation first, then the actual action.
    """
