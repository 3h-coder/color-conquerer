from enum import StrEnum, auto


class AppConfigKeys(StrEnum):
    def _generate_next_value_(name, start, count, last_values):
        return name

    SESSION_TYPE = auto()
    SESSION_REDIS = auto()
    SESSION_CACHELIB = auto()
    SESSION_KEY_PREFIX = auto()
    SESSION_COOKIE_SECURE = auto()
    SESSION_COOKIE_SAMESITE = auto()
    SESSION_PERMANENT = auto()
    SECRET_KEY = auto()
    PERMANENT_SESSION_LIFETIME = auto()


class AppSessionType(StrEnum):
    REDIS = "redis"
    CACHELIB = "cachelib"
