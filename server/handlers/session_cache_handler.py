from config.logging import get_configured_logger


class SessionCacheHandler:
    """
    Class used to store session values to retrieve when the session
    fails to properly persist between requests.
    """

    def __init__(self):
        self.logger = get_configured_logger(__name__)
        self._cache = {}

    def create_cache_for_session(self, session_id: str):
        self._cache[session_id] = {}

    def get_cache_for_session(self, session_id: str) -> dict | None:
        try:
            return self._cache[session_id]
        except KeyError:
            self.logger.error(
                f"Could not get the cache for the session {session_id} as it does not exist"
            )
