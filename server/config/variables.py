from enum import Enum


class RequiredVariables(Enum):
    DEBUG = 1
    APP_SECRET_KEY = 2
    APP_SESSION_LIFETIME = 3
    MAX_ROOM_CAPACITY = 4


class OptionalVariables(Enum):
    APP_SESSION_FILE_DIR = 1
    RESET_SESSION_FILE_ON_STARTUP = 2
