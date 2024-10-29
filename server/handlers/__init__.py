from handlers.connection_handler import ConnectionHandler
from handlers.match_handler import MatchHandler
from handlers.room_handler import RoomHandler
from handlers.session_cache_handler import SessionCacheHandler

connection_handler = ConnectionHandler()
room_handler = RoomHandler()
match_handler = MatchHandler()
session_cache_handler = SessionCacheHandler()
