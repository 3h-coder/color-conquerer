from enum import Enum, StrEnum


class RequiredVariable(Enum):
    DEBUG = 1
    CORS_ALLOWED_ORIGINS = 2
    APP_SECRET_KEY = 3
    APP_SESSION_LIFETIME_IN_S = 4
    APP_REDIS_SESSION_STORAGE = 5
    APP_POSTGRES_USER = 6
    APP_POSTGRES_PASSWORD = 7
    APP_POSTGRES_HOST = 8
    APP_POSTGRES_PORT = 9
    APP_POSTGRES_DB_NAME = 10
    FRONTEND_SERVER_PORT = 11
    BACKEND_SERVER_PORT = 12
    GAME_MAX_ROOM_CAPACITY = 13


class OptionalVariable(Enum):
    APP_SESSION_FILE_DIR = 1
    APP_REDIS_SERVER_PORT = 2
    RESET_SESSION_FILE_ON_STARTUP = 3
    RUN_TESTS_ON_STARTUP = 4


class EnvironmentVariable(StrEnum):
    """
    Should be set in the machine's environment to configure the application.
    """

    LOGS_PATH = "COLOR_CONQUERER_LOGS_PATH"
    CONFIG_PATH = "COLOR_CONQUERER_CONFIG_PATH"
