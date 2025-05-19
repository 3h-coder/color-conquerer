from config.logging import get_configured_logger


class SessionCacheHandler:
    """
    Class used to store session values to retrieve when the session
    fails to properly persist between requests (ofen happens when a redirect comes right after a session save).

    ⚠️ This auxiliary session cache is suitable for session storages that are tied to the app's
    instance lifetime (example : file system session storage during development).
    It becomes irrelevant as soon as we want to use separate session data stores that persist between app restarts (i.e. redis)
    """

    def __init__(self, enabled: bool):
        self.logger = get_configured_logger(__name__)
        self.enabled = enabled
        self._cache = {}

    def create_cache_for_session(self, session_id: str):
        if self.enabled:
            self._cache[session_id] = {}

    def get_cache_for_session(self, session_id: str) -> dict | None:
        if not self.enabled:
            return {}

        try:
            return self._cache[session_id]
        except KeyError:
            self.logger.error(
                f"Could not get the cache for the session {session_id} as it does not exist"
            )
